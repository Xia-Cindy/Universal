# Universe OS

Universe OS is a personal learning and knowledge workspace. Its single local
user entry is the interactive room at:

```text
http://127.0.0.1:5180/
```

The room is a React/Three.js client backed by the Universe API. It does not
create a second data store or AI system: Study, Knowledge, Wordbook, Work and
Novel actions continue to use the existing backend services and migrations.

## Current delivered capabilities

### Spatial entry and navigation

- The **monitor screen** enters Study Home, Goals and Tutor. The Planning Table
  enters Plan, Review and Analytics; the Knowledge Bookshelf enters Knowledge
  and Wordbook; the wall blackboard enters the review gallery.
- Every room module has a shareable route and the bottom dock offers the same
  destinations as a shortcut. The old full-desk white hotspot frame is removed.
- The normal launcher starts only the API and this room entry. The older Vue
  source remains in the repository for contract/migration tests but is not a
  runnable product entry.

### Study, Knowledge and review

- Study supports Goals, plans, tasks, sessions, learning events, review items
  and current-Goal progress aggregation through the existing API.
- Completing a Study Session atomically records the session, its linked task,
  one learning event and two scoped memory facts. Repeated or concurrent finish
  requests retain the first completed result instead of duplicating progress.
- Each uploaded Knowledge document appears as one physical book. The shelf shows
  three books at a time, supports additional shelf pages, subject filtering,
  Goal association, editing and confirmed deletion.
- A selected book opens only after its cover is clicked. The physical reader
  uses a scroll-free paired-page spread, with previous/next turns, page-number
  jump and browser-local bookmarks.
- A selected passage can become a source-document-owned note or recall card.
  Cards can hide key terms, reveal the answer and be marked `背过了`; the first
  mastery event contributes once to the linked Goal progress. Recall cards also
  show an explainable next-review date and allow a learner to manually adjust it.
- The blackboard route `/study/cards` contains only these cards and notes. It
  keeps their original document ownership and presents them in an expandable
  hanging-card gallery.
- A Study document linked to a Goal can be explicitly granted to one or more
  active Work Tech Stacks from its reader. Work receives a read-only reference
  to the original document; revoke, Goal changes, Tech Stack archival and
  source-document deletion remove that access without copying Knowledge data.

### Wordbook, Work and writing

- Wordbook tags are physical vocabulary books in the same reader. Word pages
  retain pronunciation, personal meaning, phrases, examples and notes; memory
  cards flip from English to the learner meaning and record `背过了` or `记错了`.
  The same durable recall schedule supplies the next-review date, reason and
  learner override without changing the original Wordbook record.
- Work retains Tech Stack, linked Knowledge, projects, articles, learning
  records and resume-draft APIs. Novel provides persisted draft creation and
  editing. Neither introduces a new AI Core or a separate Knowledge system.

### Persistence and RAGFlow boundary

- PostgreSQL is the normal runtime persistence adapter; SQLite remains an
  explicit local/test compatibility option.
- The RAGFlow provider adapter can upload, poll, retry, delete and retrieve
  provider-backed Knowledge documents. Processing documents keep a truthful
  status, and any returned chunks remain readable. A controlled local F1
  acceptance set (TXT, Markdown and one-page PDF) completed with nonzero
  chunks, provider retrieval and Tutor source links on 2026-08-13. This is
  local runtime evidence, not a guarantee that every existing long document
  or another provider will complete without its own validation.

## Start locally

Configure PostgreSQL in `docker/universe.env` (copy the provided example; do
not commit the local file), then run:

```bash
cd /Users/xiaxin/Documents/Codex/Universal
./startup.sh
```

The script starts the API at `http://127.0.0.1:8000` and the only product entry
at `http://127.0.0.1:5180/`. API documentation is available at
`http://127.0.0.1:8000/docs`.

To stop the local services:

```bash
./shutdown.sh
```

## Validate

```bash
python3 -m unittest discover -s tests
python3 scripts/smoke_spatial_routes.py
cd room-portfolio && npm install && npm run build
```

## Documentation

- [Information architecture](docs/02_INFORMATION_ARCHITECTURE.md)
- [Technical architecture](docs/04_TECH_ARCHITECTURE.md)
- [RAGFlow installation](docs/06_RAGFLOW_INSTALLATION.md)
- [Implementation history](docs/08_IMPLEMENTATION_HISTORY_SUMMARY.md)
- [Dated delivery roadmap](docs/10_DELIVERY_ROADMAP_2026-08-09.md)
- [Current capability review and gaps](docs/10_PLATFORM_CAPABILITIES_AND_GAPS.md)
- [Code optimization and feature plan](docs/12_OPTIMIZATION_AND_FEATURE_PLAN_2026-08-12.md)
