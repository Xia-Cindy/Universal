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

The source of truth lives in `AGENTS.md` and `docs/`.

## Test

Run the dependency-light foundation tests:

```bash
python3 -m unittest discover -s tests
```

Frontend files are scaffolded for Vue 3 / Vite, but dependencies are not installed in this milestone.

