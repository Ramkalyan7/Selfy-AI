alter table public.user_onboarding_profiles
drop constraint if exists user_onboarding_profiles_top_values_check;

alter table public.user_onboarding_profiles
add constraint user_onboarding_profiles_top_values_check
check (cardinality(top_values) = 3);
