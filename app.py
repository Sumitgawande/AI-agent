from flask import Flask, request, jsonify
import requests
import json
import mysql.connector

app = Flask(__name__)

# --- Configuration ---
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# MODEL = "anthropic/claude-3.7-sonnet"
MODEL = "openai/gpt-4.1"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Admin@123",
    "database": "classicmodels"
}

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

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("question", "")
    messages = [{"role": "user", "content": user_message}]
    tools = [{
    "type": "function",
    "function": {
        "name": "run_sql",
        "description": "Executes a SQL query on the classicmodels MySQL database.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute."
                        }
                        },
            "required": ["query"]
                    }
                }
    }]

    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "max_tokens": 500
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # ...existing code...
    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()
    print("OpenRouter response:", data)  # Debug print

    if "choices" not in data:
        return jsonify({
            "error": data.get("error", "No 'choices' in response"),
            "raw_response": data
        }), 500

    reply = data["choices"][0]["message"]
    # ...existing code...

    # If Claude wants to call the tool
    if reply.get("tool_calls"):
        print("Tool call received:", reply["tool_calls"][0])
        tool_call = reply["tool_calls"][0]
        arguments_raw = tool_call["function"]["arguments"]
        arguments = json.loads(arguments_raw)
        sql_query = arguments["query"]

        sql_result = execute_sql(sql_query)
        # Send the result back to Claude for a final answer
        tool_call_id = reply["tool_calls"][0]["id"]
        followup_payload = {
            "model": MODEL,
            "messages": messages + [
                {"role": "assistant", "tool_calls": reply["tool_calls"]},
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": "run_sql",
                    "content": str(sql_result)
                }
            ],
            "max_tokens": 500
        }
        followup = requests.post(API_URL, headers=headers, json=followup_payload)
        followup_data = followup.json()
        final_answer = followup_data["choices"][0]["message"]["content"]
        return jsonify({"answer": final_answer, "sql": sql_query, "result": sql_result})
    else:
        return jsonify({"answer": reply["content"]})

if __name__ == "__main__":
    app.run(debug=True) 