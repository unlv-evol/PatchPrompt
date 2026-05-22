# Docker Reproduction

This package includes a Dockerfile and a lightweight `docker-compose.yml` for artifact evaluators who prefer containerized execution.

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
