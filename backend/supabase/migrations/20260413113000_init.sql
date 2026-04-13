create extension if not exists pgcrypto;

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    email text not null unique,
    full_name text not null,
    password_hash text not null,
    created_at timestamptz not null default timezone('utc', now())
);
