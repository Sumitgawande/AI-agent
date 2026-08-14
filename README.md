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

For Postgres, set `DATABASE_URL` to a live connection string such as:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_agent
```

If `DATABASE_URL` is unset, the app falls back to a local SQLite file for development.

The `.env` file is ignored by Git via [.gitignore](.gitignore) so secrets and local settings stay out of version control.

## Architecture

Below is a simplified architecture diagram for Phase 1 showing the clear separation between the API, service layer, agent, LLM providers, and tools.

```mermaid
flowchart LR
	Client[Client]
	subgraph API
		direction TB
		FastAPI[FastAPI API]
	end

	subgraph App
		direction TB
		Schemas[Schemas (Pydantic)]
		Services[Services (Application layer)]
		Agent[Agent (business logic)]
		Tools[Tools]
		LLM[LLM Providers]
	end

	Client --> FastAPI
	FastAPI --> Schemas
	FastAPI --> Services
	Services --> Agent
	Agent --> Tools
	Agent --> LLM

	subgraph Providers
		direction LR
		OpenAI[OpenAI]
		Anthropic[Anthropic]
		Bedrock[Bedrock]
	end

	LLM --> OpenAI
	LLM --> Anthropic
	LLM --> Bedrock

```

Notes:
- The API layer (FastAPI) only handles HTTP, validation, and routing — it delegates business logic to the Services layer.
- `Services` orchestrate calls to the `Agent` and map domain models to transport schemas.
- `Agent` interacts with `LLM Providers` through a provider abstraction (`LLMProvider`) so provider implementations do not leak into business logic.
- `LLM_PROVIDER` environment variable controls which provider the factory returns at runtime.

Rendered diagrams (if your platform supports SVG/Mermaid):

- Architecture diagram: ![architecture](docs/architecture.svg)
- Sequence diagram: ![sequence](docs/sequence.svg)

If you want rendered SVGs locally, install the Mermaid CLI and run:

```bash
# install once (node + npm required)
npx @mermaid-js/mermaid-cli@10.3.1 --version

# generate rendered SVGs from source
npx @mermaid-js/mermaid-cli -i docs/architecture.mmd -o docs/architecture.svg
npx @mermaid-js/mermaid-cli -i docs/sequence.mmd -o docs/sequence.svg
```

I added the Mermaid source files at `docs/architecture.mmd` and `docs/sequence.mmd` plus placeholder SVGs. If you want, I can generate real SVGs here if you provide a way to install `@mermaid-js/mermaid-cli` into the environment or I can run it locally on your machine.

