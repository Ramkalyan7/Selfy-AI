# Backend

Minimal FastAPI backend scaffold for a Pika-style AI application.

The backend now uses Supabase as the single backend platform for:

- SQL data through Supabase table APIs
- Object storage through Supabase Storage buckets
- LLM access through LangChain, with Gemini configured as the first provider

## Structure

```text
backend/
|-- app/
|   |-- agent/          # Agent tools and orchestration primitives
|   |-- core/           # Settings and shared app primitives
|   |-- db/             # Supabase client setup
|   |-- integrations/   # Third-party API clients (GitHub, X, etc.)
|   |-- models/         # Domain models
|   |-- repositories/   # Supabase-backed data access
|   |-- routers/        # Feature-based HTTP routers
|   |-- schemas/        # Request/response schemas
|   `-- services/       # Business logic
|-- supabase/
|   `-- migrations/     # Supabase SQL migrations
|-- tests/              # API and service tests
|-- .env.example
|-- main.py             # Local run entrypoint
`-- pyproject.toml
```

## Run

```bash
uv sync
uv run python main.py
```

Set the Supabase settings in `backend/.env`.

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-service-role-or-server-key
SUPABASE_USERS_TABLE=users
SUPABASE_ONBOARDING_TABLE=user_onboarding_profiles
SUPABASE_ASSETS_BUCKET=assets
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
GITHUB_API_TOKEN=your-github-api-token
GITHUB_API_URL=https://api.github.com
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Create the schema through Supabase migrations, not manual SQL edits.

Initial setup:

```bash
supabase login
supabase link --project-ref your-project-ref
supabase db push
```

The initial tables are defined in [supabase/migrations/20260413113000_init.sql](./supabase/migrations/20260413113000_init.sql).

For future schema changes:

```bash
supabase migration new add_user_avatar
```

Then add SQL such as:

```sql
alter table public.users add column avatar_url text;
```

Apply migrations with:

```bash
supabase db push
```

Health check:

```text
GET /health
```

Auth endpoints:

```text
POST /auth/signup
POST /auth/login
GET /onboarding
PUT /onboarding
POST /llm/generate
```

LLM setup:

- Uses LangChain as the application-facing LLM integration layer.
- Reads the default provider from `LLM_PROVIDER`.
- Gemini credentials come from `GEMINI_API_KEY`.
- Defaults to `GEMINI_MODEL=gemini-2.5-flash`.
- `POST /llm/generate` accepts the user prompt plus optional `provider` and `model`.
- The system prompt is built on the server from the saved onboarding profile.

Agent tools:

- Third-party API clients live under `app/integrations/`.
- LangChain-compatible tool wrappers live under `app/agent/tools/`.
- The central tool registry is `app/agent/tools/registry.py`.
- GitHub is the first integration and currently provides:
  - authenticated user lookup
  - repository listing
  - repository detail lookup
  - issue creation

## Notes

- Signup and login now persist users through Supabase instead of a direct Postgres connection.
- JWT issuance is still handled by the backend application.
- Storage configuration is defined in settings so future modules can use the same Supabase project.
- Table creation and later schema changes should be committed as SQL migration files under `backend/supabase/migrations/`.
