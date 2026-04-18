

create table users (

    id uuid primary key,

    person_code varchar(100) unique not null,

    full_name varchar(200) not null,

    is_active boolean not null default true,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()

);

create extension if not exists vector;

create table face_embeddings (

    id uuid primary key,

    user_id uuid not null references users(id) on delete cascade,

    embedding vector(512) not null,

    created_at timestamptz not null default now()

);


create table attendance_logs (

    id uuid primary key,

    user_id uuid not null references users(id) on delete cascade,

    confidence double precision not null,

    attendance_date date not null,

    recognized_at timestamptz not null default now(),

    device_id varchar(100),

    created_at timestamptz not null default now(),

    unique (user_id, attendance_date)

);