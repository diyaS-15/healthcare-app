-- ============================================================================
-- Blood Report AI - Complete Database Schema
-- Deployed on Supabase PostgreSQL
-- All sensitive data encrypted with AES-256
-- Row-Level Security (RLS) enforced for privacy
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ━━━━━━━━━━━━━━ USERS TABLE ━━━━━━━━━━━━━━
-- Stores user profiles linked to Supabase Auth users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can see their own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);


-- ━━━━━━━━━━━━━━ BLOOD REPORTS TABLE ━━━━━━━━━━━━━━
-- Stores uploaded blood report metadata
CREATE TABLE IF NOT EXISTS blood_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    file_name TEXT,
    raw_text TEXT,  -- AES-256 encrypted on storage
    status TEXT CHECK (status IN ('pending', 'processed', 'analyzed')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_blood_reports_user_date ON blood_reports(user_id, report_date DESC);

ALTER TABLE blood_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see only their own reports"
    ON blood_reports FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can upload reports"
    ON blood_reports FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reports"
    ON blood_reports FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own reports"
    ON blood_reports FOR DELETE
    USING (auth.uid() = user_id);


-- ━━━━━━━━━━━━━━ BLOOD MARKERS TABLE ━━━━━━━━━━━━━━
-- Individual markers from each report
-- Normalized marker names (hemoglobin, glucose, etc.)
CREATE TABLE IF NOT EXISTS blood_markers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES blood_reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    marker_name TEXT NOT NULL,  -- Normalized: "hemoglobin", "glucose", "ldl"
    value NUMERIC NOT NULL,  -- Can be encrypted
    unit TEXT,
    reference_min NUMERIC,
    reference_max NUMERIC,
    status TEXT CHECK (status IN ('low', 'normal', 'high')) DEFAULT 'normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_blood_markers_user_marker ON blood_markers(user_id, marker_name);
CREATE INDEX idx_blood_markers_report ON blood_markers(report_id);

ALTER TABLE blood_markers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see only their own markers"
    ON blood_markers FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own markers"
    ON blood_markers FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own markers"
    ON blood_markers FOR DELETE
    USING (auth.uid() = user_id);


-- ━━━━━━━━━━━━━━ TREND ANALYSIS TABLE ━━━━━━━━━━━━━━
-- Cached trend analysis results (updated periodically)
-- Markers moving over time: "increasing", "decreasing", "stable"
CREATE TABLE IF NOT EXISTS trend_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    marker_name TEXT NOT NULL,
    trend_direction TEXT CHECK (trend_direction IN ('increasing', 'decreasing', 'stable', 'insufficient_data')),
    change_percent NUMERIC,
    consistency TEXT CHECK (consistency IN ('gradual', 'stable', 'volatile', 'fluctuating')),
    data_points INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, marker_name)
);

CREATE INDEX idx_trend_analysis_user ON trend_analysis(user_id);

ALTER TABLE trend_analysis ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see only their own trends"
    ON trend_analysis FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Backend can update trends"
    ON trend_analysis FOR INSERT
    WITH CHECK (auth.role() = 'service_role');


-- ━━━━━━━━━━━━━━ AI CONVERSATIONS TABLE ━━━━━━━━━━━━━━
-- Chat history with the AI
-- Messages are encrypted before storage
CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_id UUID REFERENCES blood_reports(id) ON DELETE SET NULL,
    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant')),
    content TEXT NOT NULL,  -- AES-256 encrypted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_date ON ai_conversations(user_id, created_at DESC);
CREATE INDEX idx_conversations_report ON ai_conversations(report_id);

ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see only their own conversations"
    ON ai_conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can send messages"
    ON ai_conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Backend can insert assistant messages"
    ON ai_conversations FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Users can delete their conversations"
    ON ai_conversations FOR DELETE
    USING (auth.uid() = user_id);


-- ━━━━━━━━━━━━━━ KNOWLEDGE BASE TABLE ━━━━━━━━━━━━━━
-- Educational content about blood markers
-- Used for RAG (Retrieval Augmented Generation)
-- PUBLIC - anyone can read
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    marker_name TEXT NOT NULL,
    category TEXT CHECK (category IN ('general', 'health_indicator', 'pattern')),
    title TEXT,
    content TEXT NOT NULL,
    source TEXT,  -- Medical resource attribution
    embedding VECTOR(1536),  -- For semantic search (pgvector)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_marker ON knowledge_base(marker_name);

-- No RLS - public knowledge base


-- ━━━━━━━━━━━━━━ AUDIT LOG TABLE ━━━━━━━━━━━━━━
-- Log of user actions for security and analytics
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,  -- 'upload_report', 'view_analysis', 'change_password', etc.
    details JSONB,  -- Can store encrypted details
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user_date ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action);

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see only their own audit logs"
    ON audit_log FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Backend can insert audit logs"
    ON audit_log FOR INSERT
    WITH CHECK (auth.role() = 'service_role');


-- ━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━

-- Update updated_at timestamp on changes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for blood_reports
CREATE TRIGGER update_blood_reports_updated_at BEFORE UPDATE ON blood_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for knowledge_base
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ━━━━━━━━━━━━━━ ANALYTICS VIEW ━━━━━━━━━━━━━━

-- High-level user analytics
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    u.id as user_id,
    u.email,
    COUNT(DISTINCT br.id) as total_reports,
    COUNT(DISTINCT bm.marker_name) as unique_markers,
    MAX(br.report_date) as last_report_date,
    MIN(br.report_date) as first_report_date,
    EXTRACT(DAY FROM (MAX(br.report_date) - MIN(br.report_date))) as tracking_days
FROM users u
LEFT JOIN blood_reports br ON u.id = br.user_id
LEFT JOIN blood_markers bm ON br.id = bm.report_id
GROUP BY u.id, u.email;

-- ━━━━━━━━━━━━━━ SAMPLE DATA ━━━━━━━━━━━━━━

-- Insert educational content into knowledge_base
INSERT INTO knowledge_base (marker_name, category, title, content, source) VALUES
('hemoglobin', 'health_indicator', 'What is Hemoglobin?', 
    'Hemoglobin (Hb) is a protein in red blood cells that carries oxygen throughout your body. Normal range is typically 12-16 g/dL for women and 13-18 g/dL for men. Changes over time can indicate health patterns.',
    'General Medical Education'),
    
('glucose', 'health_indicator', 'Blood Glucose Explained',
    'Glucose is the primary source of energy for your cells. Fasting glucose is typically 70-100 mg/dL. Patterns over time can help understand metabolic health.',
    'General Medical Education'),
    
('ldl', 'health_indicator', 'Understanding LDL Cholesterol',
    'LDL cholesterol helps transport fats in your body. Doctors often monitor LDL trends over time as part of cardiovascular health assessment.',
    'Cardiovascular Health'),
    
('triglycerides', 'pattern', 'What are Triglycerides?',
    'Triglycerides are a type of fat in your body and blood. They often move together with glucose and cholesterol markers. People track these as part of understanding metabolic patterns.',
    'Metabolic Health')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- DEPLOYMENT INSTRUCTIONS:
-- 
-- 1. Create a new PostgreSQL database in Supabase
-- 2. Run this entire SQL script
-- 3. pgvector extension (for vector embeddings) is auto-enabled above
-- 4. Enable RLS policies in Supabase dashboard
-- 5. Set up Supabase Auth (email/password)
-- 6. Create an anon key and service role key
-- 7. Copy .env template to .env and fill in credentials
-- 
-- ============================================================================
  encrypted_trend TEXT NOT NULL,
  last_updated    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, marker_name)
);

-- ============================================================
-- CHAT SESSIONS (conversation history)
-- ============================================================
CREATE TABLE public.chat_sessions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  report_id       UUID REFERENCES public.blood_reports(id) ON DELETE SET NULL,
  title           TEXT DEFAULT 'Health Analysis Chat',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CHAT MESSAGES (encrypted)
-- ============================================================
CREATE TABLE public.chat_messages (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id      UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  role            TEXT NOT NULL,        -- 'user' | 'assistant'
  -- Encrypted message content
  encrypted_content TEXT NOT NULL,
  -- Message type for UI
  message_type    TEXT DEFAULT 'text',  -- 'text' | 'voice' | 'question'
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AUDIT LOG (security — tracks all data access)
-- ============================================================
CREATE TABLE public.audit_logs (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  action          TEXT NOT NULL,
  resource_type   TEXT,
  resource_id     UUID,
  ip_address      TEXT,
  user_agent      TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ROW LEVEL SECURITY — CRITICAL FOR DATA ISOLATION
-- ============================================================
ALTER TABLE public.profiles        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blood_reports   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marker_trends   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs      ENABLE ROW LEVEL SECURITY;

-- Profiles: users can only see/edit their own profile
CREATE POLICY "profiles_own" ON public.profiles
  FOR ALL USING (auth.uid() = id);

-- Blood reports: users can only see/edit their own reports
CREATE POLICY "reports_own" ON public.blood_reports
  FOR ALL USING (auth.uid() = user_id);

-- Marker trends: own data only
CREATE POLICY "trends_own" ON public.marker_trends
  FOR ALL USING (auth.uid() = user_id);

-- Chat sessions: own data only
CREATE POLICY "sessions_own" ON public.chat_sessions
  FOR ALL USING (auth.uid() = user_id);

-- Chat messages: own data only
CREATE POLICY "messages_own" ON public.chat_messages
  FOR ALL USING (auth.uid() = user_id);

-- Audit logs: users can only read their own logs (no insert/update/delete)
CREATE POLICY "audit_read_own" ON public.audit_logs
  FOR SELECT USING (auth.uid() = user_id);

-- ============================================================
-- AUTO-CREATE PROFILE ON SIGNUP
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- AUTO-UPDATE updated_at TIMESTAMPS
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_reports_updated_at
  BEFORE UPDATE ON public.blood_reports
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_blood_reports_user_id ON public.blood_reports(user_id);
CREATE INDEX idx_blood_reports_date    ON public.blood_reports(report_date DESC);
CREATE INDEX idx_marker_trends_user    ON public.marker_trends(user_id);
CREATE INDEX idx_chat_sessions_user    ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session ON public.chat_messages(session_id);
CREATE INDEX idx_audit_logs_user       ON public.audit_logs(user_id, created_at DESC);