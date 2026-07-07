# Universe OS

Universe OS is a personal AI operating system built around Planet-based workspaces.

Milestone 1 implements the project foundation only:

- repository structure
- backend service boundaries
- database foundation migration and seed data
- Planet registry
- Universe Portal frontend shell
- Study Workspace shell
- basic API contracts

Milestone 2 adds the Study Planet learning workflow foundation:

- Goal management
- Learning Plan and Daily Tasks
- Study Session recording
- Study Home progress aggregation

Milestone 3 adds the AI Core and Tutor foundation:

- shared AI Core service entry point
- deterministic LLM Gateway for local tests
- Prompt Manager, Context Manager, and Agent Manager
- Study Tutor as an AI Core consumer
- Learning Events for Tutor interactions

Milestone 3 does not implement RAG, embeddings, Knowledge Graph, document retrieval, or source citations.

Milestone 3.5 generalizes AI Core boundaries:

- AgentDefinition registry
- context provider architecture
- prompt-key registry
- provider-only LLM Gateway input/output
- ToolRouter / Tool / Retriever interfaces only

The source of truth lives in `AGENTS.md` and `docs/`.

## Test

Run the dependency-light foundation tests:

```bash
python3 -m unittest discover -s tests
```

Frontend files are scaffolded for Vue 3 / Vite, but dependencies are not installed in this milestone.
