# Docker Reproduction

This package includes a Dockerfile and a lightweight `docker-compose.yml` for users who prefer containerized execution.

Docker is optional. The canonical evaluator path remains the local Makefile workflow:

```bash
make reproduce
make verify
```

## Build and run

```bash
docker build -t patchtrack-replication .
docker run --rm patchtrack-replication
```

Or with Docker Compose:

```bash
docker compose up --build
```

The container runs:

```bash
make reproduce && make verify
```

## Notes

- The package does not require network access after dependencies are available in the image.
- Generated outputs are written to `results/` inside the container.
- For local development, bind-mount the repository if you want generated files to persist outside the container.
- If Docker is unavailable in your evaluation environment, skip this page and use the local path in `README.md` and `docs/reproduction_steps.md`.
