-- ============================================================================
-- HealthLens Database Schema - User Management & Healthcare Data
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. USERS TABLE - User profiles with health information
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  date_of_birth DATE,
  gender VARCHAR(20), -- 'male', 'female', 'other', 'prefer_not_to_say'
  phone_number VARCHAR(20),
  
  -- Health Profile
  blood_type VARCHAR(5), -- 'O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'
  medical_conditions TEXT[] DEFAULT '{}', -- Array of conditions
  medications TEXT[] DEFAULT '{}', -- Array of current medications
  allergies TEXT[] DEFAULT '{}', -- Array of allergies
  
  -- Preferences
  notification_enabled BOOLEAN DEFAULT TRUE,
  notification_email BOOLEAN DEFAULT TRUE,
  preferred_language VARCHAR(10) DEFAULT 'en',
  units_system VARCHAR(10) DEFAULT 'metric', -- 'metric' or 'imperial'
  
  -- Account
  profile_completeness DECIMAL(3,1) DEFAULT 0, -- 0-100%
  is_verified BOOLEAN DEFAULT FALSE,
  verification_token VARCHAR(255),
  verification_token_expires_at TIMESTAMP,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP,
  
  -- Encryption
  encryption_key_salt VARCHAR(255),
  
  CONSTRAINT users_id_fk FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);

-- Enable RLS for users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view/edit their own profile
CREATE POLICY "Users can view own profile" 
  ON users FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- ============================================================================
-- 2. BLOOD_REPORTS TABLE - Uploaded medical documents
-- ============================================================================
CREATE TABLE IF NOT EXISTS blood_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- File information
  file_name VARCHAR(255) NOT NULL,
  file_path VARCHAR(500),
  file_size_bytes INTEGER,
  mime_type VARCHAR(50),
  
  -- Report metadata
  report_date DATE NOT NULL,
  lab_name VARCHAR(255),
  test_type VARCHAR(100), -- 'comprehensive', 'basic', 'specific_panel', etc.
  
  -- Extracted content (encrypted)
  raw_text TEXT,
  ocr_confidence DECIMAL(3,2), -- 0.00 - 1.00
  
  -- Processing
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'processed', 'analyzed', 'error'
  extraction_error TEXT,
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT blood_reports_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for blood_reports
CREATE INDEX IF NOT EXISTS idx_blood_reports_user_id ON blood_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_blood_reports_report_date ON blood_reports(report_date);
CREATE INDEX IF NOT EXISTS idx_blood_reports_status ON blood_reports(status);
CREATE INDEX IF NOT EXISTS idx_blood_reports_created_at ON blood_reports(created_at DESC);

-- Enable RLS for blood_reports
ALTER TABLE blood_reports ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own reports
CREATE POLICY "Users can view own reports"
  ON blood_reports FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own reports"
  ON blood_reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reports"
  ON blood_reports FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reports"
  ON blood_reports FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- 3. BLOOD_MARKERS TABLE - Extracted lab values
-- ============================================================================
CREATE TABLE IF NOT EXISTS blood_markers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  report_id UUID NOT NULL REFERENCES blood_reports(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Marker information
  marker_name VARCHAR(255) NOT NULL,
  marker_category VARCHAR(100), -- 'hematology', 'liver', 'kidney', 'lipid', etc.
  
  -- Value (encrypted in application)
  value DECIMAL(10,2),
  unit VARCHAR(50),
  
  -- Reference ranges
  reference_min DECIMAL(10,2),
  reference_max DECIMAL(10,2),
  reference_range_text VARCHAR(255),
  
  -- Status
  status VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high'
  is_critical BOOLEAN DEFAULT FALSE,
  
  -- AI Analysis
  confidence_score DECIMAL(3,2), -- 0.00 - 1.00 (confidence in extraction)
  ai_interpretation TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT blood_markers_report_fk FOREIGN KEY (report_id) REFERENCES blood_reports(id) ON DELETE CASCADE,
  CONSTRAINT blood_markers_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for blood_markers
CREATE INDEX IF NOT EXISTS idx_blood_markers_report_id ON blood_markers(report_id);
CREATE INDEX IF NOT EXISTS idx_blood_markers_user_id ON blood_markers(user_id);
CREATE INDEX IF NOT EXISTS idx_blood_markers_marker_name ON blood_markers(marker_name);
CREATE INDEX IF NOT EXISTS idx_blood_markers_status ON blood_markers(status);
CREATE INDEX IF NOT EXISTS idx_blood_markers_created_at ON blood_markers(created_at DESC);

-- Enable RLS for blood_markers
ALTER TABLE blood_markers ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own markers
CREATE POLICY "Users can view own markers"
  ON blood_markers FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================================================
-- 4. MARKER_TRENDS TABLE - Historical trends for markers
-- ============================================================================
CREATE TABLE IF NOT EXISTS marker_trends (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Marker info
  marker_name VARCHAR(255) NOT NULL,
  marker_category VARCHAR(100),
  
  -- Trend analysis
  trend_direction VARCHAR(50), -- 'increasing', 'decreasing', 'stable'
  change_percent DECIMAL(5,2), -- Percentage change over period
  consistency VARCHAR(50), -- 'gradual', 'stable', 'volatile'
  
  -- Data points
  data_points_count INTEGER DEFAULT 0,
  date_range_start DATE,
  date_range_end DATE,
  
  -- Statistics
  average_value DECIMAL(10,2),
  min_value DECIMAL(10,2),
  max_value DECIMAL(10,2),
  std_deviation DECIMAL(10,2),
  
  -- Predictions
  predicted_next_value DECIMAL(10,2),
  prediction_confidence DECIMAL(3,2),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT marker_trends_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for marker_trends
CREATE INDEX IF NOT EXISTS idx_marker_trends_user_id ON marker_trends(user_id);
CREATE INDEX IF NOT EXISTS idx_marker_trends_marker_name ON marker_trends(marker_name);
CREATE INDEX IF NOT EXISTS idx_marker_trends_updated_at ON marker_trends(updated_at DESC);

-- Enable RLS for marker_trends
ALTER TABLE marker_trends ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view their own trends
CREATE POLICY "Users can view own trends"
  ON marker_trends FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================================================
-- 5. AI_CONVERSATIONS TABLE - Chat history
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  report_id UUID REFERENCES blood_reports(id) ON DELETE SET NULL,
  
  -- Conversation metadata
  conversation_id UUID, -- Group related messages
  message_type VARCHAR(50), -- 'user_message', 'ai_response', 'system'
  
  -- Content (encrypted in application)
  content TEXT NOT NULL,
  
  -- Metadata
  token_count INTEGER, -- For usage tracking
  model_used VARCHAR(50), -- 'gpt-4o', 'gpt-3.5-turbo', etc.
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT ai_conversations_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT ai_conversations_report_fk FOREIGN KEY (report_id) REFERENCES blood_reports(id) ON DELETE SET NULL
);

-- Create indexes for ai_conversations
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_conversation_id ON ai_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_report_id ON ai_conversations(report_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_at ON ai_conversations(created_at DESC);

-- Enable RLS for ai_conversations
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own conversations
CREATE POLICY "Users can view own conversations"
  ON ai_conversations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own conversations"
  ON ai_conversations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- 6. HEALTH_NOTES TABLE - User's personal health notes
-- ============================================================================
CREATE TABLE IF NOT EXISTS health_notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  report_id UUID REFERENCES blood_reports(id) ON DELETE SET NULL,
  
  -- Note content
  title VARCHAR(255),
  content TEXT NOT NULL,
  note_type VARCHAR(50), -- 'symptom', 'medication', 'observation', 'goal', 'general'
  
  -- Metadata
  is_pinned BOOLEAN DEFAULT FALSE,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT health_notes_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT health_notes_report_fk FOREIGN KEY (report_id) REFERENCES blood_reports(id) ON DELETE SET NULL
);

-- Create indexes for health_notes
CREATE INDEX IF NOT EXISTS idx_health_notes_user_id ON health_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_health_notes_note_type ON health_notes(note_type);
CREATE INDEX IF NOT EXISTS idx_health_notes_created_at ON health_notes(created_at DESC);

-- Enable RLS for health_notes
ALTER TABLE health_notes ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own notes
CREATE POLICY "Users can manage own notes"
  ON health_notes FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 7. AUDIT_LOG TABLE - Activity tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Action
  action VARCHAR(100) NOT NULL, -- 'upload_report', 'view_analysis', 'chat_message', 'profile_update', etc.
  resource_type VARCHAR(50), -- 'report', 'marker', 'profile', 'settings'
  resource_id UUID,
  
  -- Details (encrypted in application)
  details TEXT,
  
  -- Status
  status VARCHAR(50), -- 'success', 'failure'
  error_message TEXT,
  
  -- IP and user agent
  ip_address VARCHAR(50),
  user_agent TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT audit_log_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for audit_log
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at DESC);

-- Enable RLS for audit_log
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view their own audit log
CREATE POLICY "Users can view own audit log"
  ON audit_log FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================================================
-- 8. KNOWLEDGE_BASE TABLE - Medical information for RAG
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_base (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Content
  marker_name VARCHAR(255) NOT NULL,
  category VARCHAR(100), -- 'hematology', 'liver', 'kidney', etc.
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  source VARCHAR(255),
  
  -- Medical information
  normal_range_text VARCHAR(255),
  high_values_meaning TEXT,
  low_values_meaning TEXT,
  clinical_significance TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(marker_name, title)
);

-- Create indexes for knowledge_base
CREATE INDEX IF NOT EXISTS idx_knowledge_base_marker_name ON knowledge_base(marker_name);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);

-- Knowledge base is public (no RLS needed)
ALTER TABLE knowledge_base DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 9. USER_SETTINGS TABLE - User preferences
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Notifications
  email_on_critical_marker BOOLEAN DEFAULT TRUE,
  email_on_new_insights BOOLEAN DEFAULT TRUE,
  email_on_trend_changes BOOLEAN DEFAULT TRUE,
  email_on_weekly_summary BOOLEAN DEFAULT TRUE,
  
  -- Display preferences
  theme VARCHAR(20) DEFAULT 'light', -- 'light', 'dark'
  show_advanced_metrics BOOLEAN DEFAULT FALSE,
  
  -- Data sharing
  allow_research_participation BOOLEAN DEFAULT FALSE,
  data_sharing_level VARCHAR(50) DEFAULT 'private', -- 'private', 'doctors', 'family'
  
  -- Privacy
  two_factor_enabled BOOLEAN DEFAULT FALSE,
  require_password_on_sensitive BOOLEAN DEFAULT TRUE,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT user_settings_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for user_settings
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- Enable RLS for user_settings
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only manage their own settings
CREATE POLICY "Users can manage own settings"
  ON user_settings FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 10. DEVICE_SESSIONS TABLE - Track user devices and logins
-- ============================================================================
CREATE TABLE IF NOT EXISTS device_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Device info
  device_name VARCHAR(255),
  device_type VARCHAR(50), -- 'web', 'mobile', 'tablet'
  os VARCHAR(100),
  browser VARCHAR(100),
  
  -- Session
  session_token VARCHAR(255) UNIQUE,
  ip_address VARCHAR(50),
  
  -- Activity
  last_active_at TIMESTAMP,
  is_current BOOLEAN DEFAULT TRUE,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  
  CONSTRAINT device_sessions_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for device_sessions
CREATE INDEX IF NOT EXISTS idx_device_sessions_user_id ON device_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_device_sessions_is_current ON device_sessions(is_current);

-- Enable RLS for device_sessions
ALTER TABLE device_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own device sessions
CREATE POLICY "Users can view own device sessions"
  ON device_sessions FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to update user updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_user_timestamp();

-- Trigger for blood_reports
CREATE TRIGGER blood_reports_updated_at
  BEFORE UPDATE ON blood_reports
  FOR EACH ROW
  EXECUTE FUNCTION update_user_timestamp();

-- Trigger for marker_trends
CREATE TRIGGER marker_trends_updated_at
  BEFORE UPDATE ON marker_trends
  FOR EACH ROW
  EXECUTE FUNCTION update_user_timestamp();

-- Trigger for health_notes
CREATE TRIGGER health_notes_updated_at
  BEFORE UPDATE ON health_notes
  FOR EACH ROW
  EXECUTE FUNCTION update_user_timestamp();

-- Trigger for user_settings
CREATE TRIGGER user_settings_updated_at
  BEFORE UPDATE ON user_settings
  FOR EACH ROW
  EXECUTE FUNCTION update_user_timestamp();

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_blood_markers_user_marker ON blood_markers(user_id, marker_name);
CREATE INDEX IF NOT EXISTS idx_blood_reports_user_date ON blood_reports(user_id, report_date DESC);
CREATE INDEX IF NOT EXISTS idx_marker_trends_user_date ON marker_trends(user_id, date_range_end DESC);
CREATE INDEX IF NOT EXISTS idx_health_notes_user_date ON health_notes(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user_date ON ai_conversations(user_id, created_at DESC);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert sample health markers knowledge base
INSERT INTO knowledge_base (marker_name, category, title, content, normal_range_text, high_values_meaning, low_values_meaning, clinical_significance)
VALUES
  ('Hemoglobin', 'Hematology', 'Red Blood Cell Protein', 
   'Hemoglobin (Hb) is the iron-rich protein in red blood cells that carries oxygen throughout the body.',
   'Male: 13.5-17.5 g/dL, Female: 12.0-15.5 g/dL',
   'High hemoglobin (polycythemia) can indicate dehydration, smoking, or bone marrow disorders.',
   'Low hemoglobin (anemia) may indicate iron deficiency, vitamin deficiencies, or chronic disease.',
   'Critical indicator of oxygen-carrying capacity and overall health status.'),
  
  ('Glucose', 'Metabolic', 'Blood Sugar Level',
   'Glucose is the primary source of energy for cells. Blood glucose levels are carefully regulated by insulin and glucagon.',
   'Fasting: 70-100 mg/dL, Random: <140 mg/dL',
   'High glucose (hyperglycemia) may indicate diabetes, metabolic syndrome, or other endocrine disorders.',
   'Low glucose (hypoglycemia) can cause dizziness, sweating, and in severe cases, seizures.',
   'Essential indicator for diabetes screening and management.'),
  
  ('Total Cholesterol', 'Lipid Profile', 'Total Blood Cholesterol',
   'Cholesterol is a waxy substance needed for cell function but can accumulate in arteries, increasing heart disease risk.',
   '<200 mg/dL: Desirable, 200-239 mg/dL: Borderline high, ≥240 mg/dL: High',
   'High cholesterol increases risk of heart disease and stroke.',
   'Low cholesterol is rare but may indicate malnutrition or liver disease.',
   'Key marker for cardiovascular health assessment.'),
  
  ('Creatinine', 'Kidney Function', 'Kidney Function Marker',
   'Creatinine is a waste product produced by muscles and filtered by the kidneys. Elevated levels indicate reduced kidney function.',
   'Male: 0.7-1.3 mg/dL, Female: 0.6-1.1 mg/dL',
   'High creatinine indicates impaired kidney function and requires medical evaluation.',
   'Low creatinine is uncommon but may indicate reduced muscle mass.',
   'Primary indicator of kidney function and glomerular filtration rate.'),
  
  ('TSH', 'Thyroid', 'Thyroid Stimulating Hormone',
   'TSH regulates thyroid hormone production. It is elevated when thyroid hormones are low, and vice versa.',
   '0.4-4.0 mIU/L',
   'High TSH may indicate hypothyroidism or thyroid disease.',
   'Low TSH may indicate hyperthyroidism or thyroid medication overdose.',
   'Essential screening tool for thyroid disorders.')
ON CONFLICT (marker_name, title) DO NOTHING;

COMMIT;
