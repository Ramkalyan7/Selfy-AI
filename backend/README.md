# Backend

Minimal FastAPI backend scaffold for a Pika-style AI application.

The backend is wired to SQLAlchemy and expects a SQL database via `DATABASE_URL`.

## Structure

```text
backend/
├── app/
│   ├── core/           # Settings and shared app primitives
│   ├── db/             # Database setup
│   ├── models/         # ORM/domain models
│   ├── repositories/   # Data access layer
│   ├── routers/        # Feature-based HTTP routers
│   ├── schemas/        # Request/response schemas
│   └── services/       # Business logic
├── tests/              # API and service tests
├── .env.example
├── main.py             # Local run entrypoint
└── pyproject.toml
```

## Run

```bash
uv sync
uv run python main.py
```

Set `DATABASE_URL` in `.env` to switch databases.

Examples:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/selfy_ai
```

Health check:

```text
GET /health
```

## Suggested next modules

- Auth and user management
- Project/session management
- AI generation jobs and queues
- Asset storage integration
- Billing and usage tracking
