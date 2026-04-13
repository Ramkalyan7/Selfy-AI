# Backend

Minimal FastAPI backend scaffold for a Pika-style AI application.

The backend now uses Supabase as the single backend platform for:

- SQL data through Supabase table APIs
- Object storage through Supabase Storage buckets

## Structure

```text
backend/
|-- app/
|   |-- core/           # Settings and shared app primitives
|   |-- db/             # Supabase client setup
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
```

## Notes

- Signup and login now persist users through Supabase instead of a direct Postgres connection.
- JWT issuance is still handled by the backend application.
- Storage configuration is defined in settings so future modules can use the same Supabase project.
- Table creation and later schema changes should be committed as SQL migration files under `backend/supabase/migrations/`.
