from flask import Flask, request, jsonify
import requests
import json
import mysql.connector
import os

app = Flask(__name__)

API_KEY = os.environ.get("OPENROUTER_API_KEY")
print("API KEY:", API_KEY)
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4.1"  # or any Bedrock-compatible model like Claude

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.environ.get("DB_PASSWORD"),
    "database": "classicmodels"
}

# --------------------------------------------
# SQL Execution Helper
# --------------------------------------------
def execute_sql(query):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return {"columns": columns, "rows": rows}
    except Exception as e:
        return {"error": str(e)}


def make_json_safe(data):
    if isinstance(data, list):
        return [make_json_safe(item) for item in data]
    elif isinstance(data, tuple):
        return [make_json_safe(item) for item in data]
    elif isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, (int, float, str, bool)) or data is None:
        return data
    else:
        return str(data)  # fallback for things like Decimal, datetime, etc.


# --------------------------------------------
# Main Ask Endpoint
# --------------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "")
    if not user_question:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Step 1: Ask LLM to generate SQL + chartType
    messages = [
        {
            "role": "system",
            "content": """
You are an assistant that:
1. Converts natural language questions into SQL queries for a MySQL database.
2. Suggests the best chart type for visualizing the result (bar, pie, line, etc.), based on user intent or data structure.
3. If the user did not request a chart, return chartType as "null".

Return only the tool/function call with both SQL and chartType.
"""
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_sql_and_chart_type",
                "description": "Generates SQL and suggests chart type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to run"
                        },
                        "chartType": {
                            "type": "string",
                            "description": "Suggested chart type",
                            "enum": ["bar", "line", "pie", "doughnut", "radar", "scatter", "null"]
                        }
                    },
                    "required": ["query", "chartType"]
                }
            }
        }
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "max_tokens": 500
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()

    if "choices" not in data:
        return jsonify({"error": "LLM failed to respond", "raw": data}), 500

    try:
        tool_call = data["choices"][0]["message"]["tool_calls"][0]
        args = json.loads(tool_call["function"]["arguments"])
        sql_query = args["query"]
        chart_type = args["chartType"]
    except Exception as e:
        return jsonify({"error": "Failed to parse SQL or chart type", "details": str(e), "raw": data}), 500

    # Step 2: Execute SQL
    sql_result = execute_sql(sql_query)
    if "error" in sql_result:
        return jsonify({"error": "SQL execution failed", "details": sql_result}), 500

    # Step 3: If chart is requested or inferred, generate Chart.js config
    chart_config = None
    chart_json = None

    if chart_type != "null":
        chart_prompt = f"""
You are a chart generator. Given a SQL result (columns and rows) and a chart type, generate a valid Chart.js configuration object.

Chart type: {chart_type}

Respond ONLY with valid JSON config for Chart.js:
{{
  "type": "...",
  "data": {{ ... }},
  "options": {{}}
}}

"""


        print("type",type(chart_config))
        print("chart config",chart_config)
        print("sql_result",sql_result)
        safe_sql_result = make_json_safe(sql_result)
        print("Safe SQL result:", safe_sql_result)
        chart_messages = [
            {"role": "system", "content": chart_prompt},
            {"role": "user", "content": f"Here is the SQL result:\n{json.dumps(safe_sql_result)}"}
        ]

        chart_payload = {
            "model": MODEL,
            "messages": chart_messages,
            "max_tokens": 1000
        }

        chart_response = requests.post(API_URL, headers=headers, json=chart_payload)
        chart_data = chart_response.json()

        try:
            chart_json = chart_data["choices"][0]["message"]["content"]
            chart_config = json.loads(chart_json)
        except Exception as e:
            chart_config = None

    # Step 4: Return the result
    return jsonify({
        "question": user_question,
        "sql": sql_query,
        "result": sql_result,
        "chartType": chart_type,
        "chartConfig": chart_config,
        "rawChartJson": chart_json  # in case frontend wants to handle formatting
    })

# --------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
