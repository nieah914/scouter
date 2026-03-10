-- 현대인 생존 전투력 측정기 - Supabase DB 스키마
-- Supabase SQL Editor에서 실행하세요

CREATE TABLE IF NOT EXISTS users (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_token     TEXT UNIQUE NOT NULL,
    gender         TEXT,
    age            INTEGER,
    height         FLOAT,
    weight         FLOAT,
    sleep_hours    FLOAT,
    pushup_count   INTEGER,
    running_count  INTEGER,
    coffee_cups    INTEGER,
    overtime_days  INTEGER,
    diet_score     INTEGER DEFAULT 0,
    stress_score   INTEGER DEFAULT 0,
    sitting_hours  INTEGER DEFAULT 6,
    alcohol_freq   INTEGER DEFAULT 0,
    bmi            FLOAT,
    bmi_status     TEXT,
    str_score      INTEGER,
    agi_score      INTEGER,
    hp_score       INTEGER,
    debuff_score   INTEGER,
    character_id   TEXT,
    overall_grade  TEXT,
    ai_result      JSONB,
    is_paid        BOOLEAN DEFAULT FALSE,
    order_id       TEXT,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_users_user_token ON users(user_token);
CREATE INDEX IF NOT EXISTS idx_users_is_paid    ON users(is_paid);

-- RLS (Row Level Security) - 서비스 키로만 접근
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 기존 DB에 새 컬럼 추가 (이미 생성된 경우 실행)
ALTER TABLE users ADD COLUMN IF NOT EXISTS diet_score    INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stress_score  INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS sitting_hours INTEGER DEFAULT 6;
ALTER TABLE users ADD COLUMN IF NOT EXISTS alcohol_freq  INTEGER DEFAULT 0;
