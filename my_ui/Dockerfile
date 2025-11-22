FROM python:3.13-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/streamlit", "run", "ui_main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# docker build -f Dockerfile -t ui-app .
# docker run -p 8501:8501 ui-app