# Universe OS Development Rules

Version: 1.0

Project:

Universe OS

Purpose:

Define development rules and constraints for AI coding agents.

---

# 1. Project Identity

Universe OS is an AI Personal Operating System.

The system consists of:

- AI CORE

- Multiple Planets

- Planet Agents

- Memory System

- Knowledge System

- User Profile

The first implementation target is:

Study Planet

Do not expand to other Planets unless explicitly requested.

---

# 2. Source Of Truth

The product specification is defined by:

```

docs/

```

All Markdown files inside docs are the source of truth.

Before modifying code:

- Read relevant documentation.

- Follow documented architecture.

- Do not replace requirements with assumptions.

If code conflicts with documentation, follow documentation.

---

# 3. Before Coding

Before implementing any feature:

1. Read related documents.

2. Understand:

   - purpose

   - architecture

   - data flow

   - dependencies

3. Produce an implementation plan.

4. Ask for clarification if requirements are unclear.

Do not guess.

---

# 4. Architecture Rules

## AI CORE

There is only one AI CORE.

Architecture:

```

AI CORE

|

+-- Study Agent

+-- Work Agent

+-- Life Agent

```

Do not create independent AI systems.

---

## Planet Architecture

Each Planet owns:

- business logic

- workflows

- domain models

Shared:

- user

- memory

- knowledge

- AI Core

---

## Agent Architecture

Agents are capabilities.

Example:

```

Study Agent

├── Planner Agent

├── Tutor Agent

├── Review Agent

├── Coach Agent

└── Analyst Agent

```

Do not merge all capabilities into one giant Agent.

---

# 5. Development Priority

Always follow:

```

Documentation

↓

Architecture

↓

Database

↓

Backend API

↓

AI Core

↓

Agents

↓

Frontend

↓

Optimization

```

---

# 6. Current Product Scope

Current target:

Study Planet MVP

Required:

- User system

- Study Goal

- Study Plan

- Daily Task

- Study Session

- Tutor / RAG Q&A

- Knowledge

- Basic Analytics

Not required yet:

- Work Planet

- Life Planet

- Mobile application

- Social features

---

# 7. Database Rules

Database must:

- use migrations

- maintain relationships

- avoid duplicate data

- separate Planet data

Before changing database:

Check:

- existing models

- API impact

- Agent impact

---

# 8. Backend Rules

Backend should use:

- modular structure

- clear service boundaries

- separated APIs

Preferred:

```

routers

services

models

schemas

agents

core

```

Avoid:

- business logic inside routes

- duplicated services

- unnecessary abstraction

---

# 9. Frontend Rules

Frontend should follow:

```

Universe Home

↓

Planet

↓

Workspace

```

Do not create unrelated dashboards.

---

# 10. AI Rules

AI features must:

- use AI CORE

- load proper context

- respect memory rules

Use:

- user profile

- memory

- knowledge

when required.

---

# 11. Memory Rules

Memory belongs to User and is separated by scope.

Approved scopes:

- global

- planet

- session

Required ownership / scope fields:

- user_id

- scope

- planet_type

- session_id

Store:

- long-term goals

- preferences

- learning history

Do not store:

- temporary conversation

- irrelevant information

---

# 12. Knowledge System Rules

Knowledge flow:

```

Document

↓

Chunk

↓

Embedding

↓

Knowledge Node

↓

Retrieval

↓

AI Response

```

Tutor and RAG Q&A should use the Knowledge System.

---

# 13. Testing Rules

Meaningful features should include:

- unit tests

- integration tests where needed

Before completion verify:

- existing features

- API behavior

- database migration

---

# 14. Documentation Rules

Keep synchronized:

- code

- documentation

- implementation status

Update:

```

docs/

README.md

CHANGELOG.md

TODO.md

```

when required.

---

# 15. Git Rules

Commit frequently.

One commit:

One logical change.

Examples:

```

feat(core): add agent router

feat(study): create study goal API

fix(api): handle validation

docs: update architecture

```

---

# 16. Ambiguity Policy

If encountering:

- unclear requirement

- architecture conflict

- missing information

Stop and report:

```

Problem:

Affected files:

Conflict:

Possible solutions:

```

Wait for instruction.

---

# 17. Forbidden Actions

Never:

- redesign architecture

- replace technology stack

- create unnecessary modules

- ignore documentation

- create duplicated systems

---

# 18. Definition Of Done

A feature is complete only when:

```

Code

+

Database

+

API

+

Tests

+

Documentation

+

Commit

```

are completed.

---

# 19. Final Objective

Build:

```

One User

+

One AI CORE

+

Multiple Intelligent Planets

+

Memory

+

Knowledge

+

Execution System

=

Personal AI Operating System

```

All implementation decisions must serve this goal.

---

# 20. Repository Structure Rules

Follow the existing repository structure.

Do not create new top-level directories without approval.

Expected structure:

```

/

├── AGENTS.md

├── docs/

├── backend/

├── frontend/

├── database/

├── docker/

└── scripts/

```

Backend:

```

backend/app/

├── core/

├── agents/

├── planets/

├── api/

├── services/

├── models/

└── schemas/

```

Frontend:

```

frontend/src/

├── pages/

├── components/

├── api/

├── stores/

└── assets/

```

Do not move files or rename major folders without approval.

---

# 21. Milestone Execution Rules

Development must follow milestone order.

Before starting a milestone, provide:

- objective

- files affected

- database changes

- API changes

- risks

- acceptance criteria

Only implement the approved milestone.

After completion update:

- TODO.md

- CHANGELOG.md

- documentation

Then continue to the next milestone.
