# AI Agent Starter

This project provides a practical foundation for a modern AI agent with:

- a tool-calling loop
- short-term memory for conversations
- support for local fallback behavior when no API key is configured
- a simple CLI for interactive use

## Features

- Plan and execute tasks in a loop
- Use built-in tools such as time lookup, calculator, and knowledge lookup
- Keep recent user context in memory
- Easily swap in an LLM backend later

## Quick start

1. Install Poetry if you do not already have it.
2. Create a virtual environment with Poetry.
3. Run the CLI.

```bash
poetry install
poetry run python -m app.agents.main
```

Alternatively, launch an interactive shell:

```bash
poetry shell
python -m app.agents.main
```

## Configuration

Copy `.env.example` to `.env` and set your preferred values.

The `.env` file is ignored by Git via [.gitignore](.gitignore) so secrets and local settings stay out of version control.
