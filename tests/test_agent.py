import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.agent import create_agent


def test_local_time_response():
    agent = create_agent()
    response = agent.run("What time is it?")
    assert "current time" in response.lower()


def test_calculator_response():
    agent = create_agent()
    response = agent.run("Calculate 2 + 2")
    assert "4" in response
