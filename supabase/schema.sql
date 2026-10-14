-- Video Jobs Table for Supabase & Fal.ai Wan v2.7 Integration

create table if not exists public.video_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id),
  request_id text not null,
  model text not null,
  mode text not null check (mode in ('text', 'image')),
  status text not null default 'queued',
  video_url text,
  created_at timestamptz not null default now(),
  unique (model, request_id)
);

-- Enable Row Level Security (RLS)
alter table public.video_jobs enable row level security;

-- Policy: Authenticated users can view their own video jobs
create policy "Users can view their own video jobs"
  on public.video_jobs
  for select
  to authenticated
  using (auth.uid() = user_id);

-- Policy: Authenticated users / functions can insert their own video jobs
create policy "Users can create their own video jobs"
  on public.video_jobs
  for insert
  to authenticated
  with check (auth.uid() = user_id);

-- Policy: Authenticated users / functions can update their own video jobs
create policy "Users can update their own video jobs"
  on public.video_jobs
  for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
