# TODO

## Milestone 1 Foundation

- [x] Align repository structure with `AGENTS.md`.
- [x] Add backend project structure and API contract boundaries.
- [x] Add database foundation migration and seed data.
- [x] Add Planet registry with Study active and Future Planet placeholders.
- [x] Add Study Home empty-state contract.
- [x] Add Study Workspace shell files.

## Milestone 2 Learning Workflow

- [x] Add Study Goal service and API contracts.
- [x] Add Learning Plan and Daily Task service contracts.
- [x] Add Study Session start/finish recording.
- [x] Add Study Home progress aggregation.
- [x] Add Study Plan frontend workflow.
- [x] Keep Knowledge, Tutor, Review, and Analytics as placeholders.

## Milestone 3 AI Core + Tutor

- [x] Add shared AI Core service entry point.
- [x] Add LLM Gateway interface and deterministic provider.
- [x] Add Prompt Manager, Context Manager, and Agent Manager.
- [x] Add Study Tutor as an AI Core consumer.
- [x] Add Tutor API and frontend page.
- [x] Record Tutor interactions as Learning Events.
- [x] Keep RAG, embeddings, Knowledge Graph, document retrieval, and source citations out of scope.

## Milestone 3.5 AI Core Generalization

- [x] Add AgentDefinition registration model.
- [x] Refactor AgentManager to resolve registered definitions.
- [x] Refactor ContextManager to use context providers.
- [x] Move Study Tutor context assembly into a Study provider.
- [x] Refactor PromptManager to resolve prompt keys.
- [x] Keep LLM Gateway provider-only.
- [x] Add ToolRouter, Tool, and Retriever interfaces only.

## Later Milestones

- [ ] Connect Study services to PostgreSQL adapters.
- [ ] Implement File Upload and Knowledge processing.
- [ ] Implement Knowledge + RAG with citations.
- [ ] Implement Memory Intelligence.
- [ ] Implement Wrong Questions, Review, and Analytics.
