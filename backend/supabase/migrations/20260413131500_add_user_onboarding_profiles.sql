create table if not exists public.user_onboarding_profiles (
    user_id uuid primary key references public.users(id) on delete cascade,
    display_name text not null,
    occupation text not null,
    personality_description text not null,
    communication_style text not null check (communication_style in ('casual', 'formal', 'mixed')),
    conflict_response_style text not null,
    top_values text[] not null check (cardinality(top_values) = 1),
    dislikes text not null,
    reply_to_invite text not null,
    reply_to_low_mood text not null,
    reply_to_help_request text not null,
    long_form_topics text not null,
    current_goals text not null,
    completed_at timestamptz not null default timezone('utc', now()),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now())
);

create or replace function public.set_user_onboarding_profiles_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = timezone('utc', now());
    new.completed_at = timezone('utc', now());
    return new;
end;
$$;

drop trigger if exists set_user_onboarding_profiles_updated_at on public.user_onboarding_profiles;

create trigger set_user_onboarding_profiles_updated_at
before update on public.user_onboarding_profiles
for each row
execute function public.set_user_onboarding_profiles_updated_at();
