FROM ghcr.io/astral-sh/uv:python3.9-bookworm-slim

WORKDIR /app


COPY . .

# Install dependencies into the uv-managed .venv
RUN uv sync --locked
RUN uv add celery
RUN pip install celery


RUN chmod +x /app/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Now copy the rest of the app code

EXPOSE 8000

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
