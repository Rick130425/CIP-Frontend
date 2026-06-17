FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "frontend/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
