# Cloud Development Deployment — 2026-08-23

## Objective

Run an isolated Universe OS development stack on the JD Cloud host without
changing its existing AI Agent, default Nginx route, PostgreSQL or Redis.

## Boundary

- Checkout: `/Universal` on the server.
- Entry: `127.0.0.1:15180` on the server, reached from the development Mac by
  an SSH tunnel. No domain, public listener or Nginx modification is used.
- Services: dedicated Universe frontend, API, PostgreSQL volume and local
  object-storage volume.
- Knowledge provider: `local` for this milestone. RAGFlow needs separate
  resource review and server-only provider secrets before it can be enabled.
- Study: the locally ignored Sylva assets are not deployed. The production
  image uses an original Study Space fallback rather than copying unlicensed
  local assets.

## Start

On the server, create `docker/development/universe.env` with mode `0600` from
the example, replacing only the PostgreSQL password with a long random value.

If the server can reach `pypi.org` with curl but Python/pip wheel downloads
time out, set `PIP_INDEX_URL` in this same `/Universal`-scoped file to a
reviewed HTTPS mirror for the build. This is passed only to Docker's API image
build argument; it does not alter the host's pip configuration or the running
containers.

```bash
cd /Universal
docker compose --env-file docker/development/universe.env \
  -f docker/development/compose.yml up -d --build
```

## Access

From the development Mac:

```bash
ssh -N -L 15180:127.0.0.1:15180 jdcloud-lavm
```

Then open `http://127.0.0.1:15180/` locally. The API remains reachable only
through the frontend proxy and is not exposed as a separate host port.

## Acceptance

- `docker compose ... ps` reports database health and running API/room services.
- `curl --fail http://127.0.0.1:15180/api/health` succeeds on the server.
- `/`, `/study`, `/study/wordbook`, `/study/cards`, `/work` and `/novel` load
  through the tunnel.
- Existing host containers and Nginx configuration remain unchanged.
