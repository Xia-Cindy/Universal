# Cloud Development Deployment — 2026-08-23

## Objective

Run an isolated Universe OS development stack on the JD Cloud host without
changing its existing AI Agent, default Nginx route, PostgreSQL or Redis.

## Boundary

- Checkout: `/Universal` on the server.
- Default entry: `127.0.0.1:15180` on the server, reached from the development
  Mac by an SSH tunnel. No domain or Nginx modification is used.
- Direct IP option: set `UNIVERSE_BIND_ADDRESS=0.0.0.0` in the private
  `/Universal/docker/development/universe.env` file. The frontend is then
  available at `http://<server-ip>:15180`; API and PostgreSQL remain internal
  to the Compose network. Allow only TCP `15180` in the cloud security group.
- Services: dedicated Universe frontend, API, PostgreSQL volume and local
  object-storage volume.
- Knowledge provider: `local` for this milestone. RAGFlow needs separate
  resource review and server-only provider secrets before it can be enabled.
- Study: the locally ignored Sylva assets are not deployed. The production
  image uses an original Study Space fallback rather than copying unlicensed
  local assets.
- Performance: the isolated room Nginx enables gzip for JavaScript/CSS and
  immutable cache headers for Vite fingerprinted `/assets/` files. The HTML
  entry remains non-cached so a new release points to new asset names.

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

For direct IP access, restart only the `room` service after setting the bind
address:

```bash
cd /Universal
docker compose --env-file docker/development/universe.env \
  -f docker/development/compose.yml up -d --no-deps room
```

Then open `http://<server-ip>:15180/`. This is plain HTTP until a domain and
TLS reverse-proxy milestone is separately approved.

## Acceptance

- `docker compose ... ps` reports database health and running API/room services.
- `curl --fail http://127.0.0.1:15180/api/health` succeeds on the server.
- `/`, `/study`, `/study/wordbook`, `/study/cards`, `/work` and `/novel` load
  through the tunnel.
- Existing host containers and Nginx configuration remain unchanged.

# Room first-screen loading (2026-08-25)

The Room entry is optimized for direct-IP access, where public bandwidth can be notably slower than the local development server:

- the entry bundle renders a local loading shell before the Three.js application chunk resolves;
- it no longer depends on a Google Fonts request before first paint;
- `PlanOrbit.glb` is no longer fetched from the Room home page and loads only when its Plan module renders;
- Nginx serves hashed `/assets/` files with immutable cache headers and gzip for text assets. Binary GLB files remain uncompressed because the primary room model did not meaningfully shrink under gzip.
