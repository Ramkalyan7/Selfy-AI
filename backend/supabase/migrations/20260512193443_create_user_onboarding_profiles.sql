ALTER TABLE public.user_onboarding_profiles
ADD COLUMN primary_language text not null,
ADD COLUMN secondary_language text not null,
ADD COLUMN industry text not null,
DROP COLUMN IF EXISTS reply_to_invite,
DROP COLUMN IF EXISTS reply_to_low_mood,
DROP COLUMN IF EXISTS conflict_response_style,
DROP COLUMN IF EXISTS reply_to_help_request;