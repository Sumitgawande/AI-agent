from __future__ import annotations

from .agent import create_agent


def main() -> None:
    agent = create_agent()
    print(f"Welcome to {agent.name}.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        response = agent.run(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
