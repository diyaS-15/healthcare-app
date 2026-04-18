"""
Database Models - Supabase SQL Tables
All medical data is AES-256 encrypted at rest.
"""

# This file documents the database schema used in Supabase
# SQL will be in migrations/001_init.sql

# TABLE: users
# - id (uuid, primary key) - Supabase auth user ID
# - email (text) - User email
# - full_name (text) - User full name
# - created_at (timestamp)
# - updated_at (timestamp)
# - encryption_key_salt (text) - For deriving user-specific encryption key

# TABLE: blood_reports
# - id (uuid, primary key)
# - user_id (uuid, foreign key → users)
# - report_date (date) - When report was taken
# - file_name (text) - Original filename
# - uploaded_at (timestamp)
# - raw_text (text, encrypted) - OCR/PDF extracted text
# - status (text) - 'pending' | 'processed' | 'analyzed'
# - created_at (timestamp)
# - updated_at (timestamp)
# RLS: Users see only their own reports

# TABLE: blood_markers
# - id (uuid, primary key)
# - report_id (uuid, foreign key → blood_reports)
# - user_id (uuid, foreign key → users)
# - marker_name (text) - Normalized name: "hemoglobin", "ldl", etc.
# - value (numeric, encrypted) - The actual lab value
# - unit (text) - "g/dL", "mg/dL", etc.
# - reference_min (numeric) - Normal range min
# - reference_max (numeric) - Normal range max
# - status (text) - 'low' | 'normal' | 'high'
# - created_at (timestamp)
# RLS: Users see only their own markers

# TABLE: trend_analysis
# - id (uuid, primary key)
# - user_id (uuid, foreign key → users)
# - marker_name (text) - Which marker this trend is for
# - trend_direction (text) - 'increasing' | 'decreasing' | 'stable'
# - change_percent (numeric) - % change over time
# - consistency (text) - 'gradual' | 'stable' | 'volatile'
# - data_points (integer) - How many reports analyzed
# - updated_at (timestamp)
# RLS: Users see only their own trends

# TABLE: ai_conversations
# - id (uuid, primary key)
# - user_id (uuid, foreign key → users)
# - report_id (uuid, foreign key → blood_reports, nullable)
# - message_type (text) - 'user' | 'assistant'
# - content (text, encrypted) - The message
# - created_at (timestamp)
# RLS: Users see only their own conversations

# TABLE: knowledge_base
# - id (uuid, primary key)
# - marker_name (text) - Which blood marker
# - category (text) - 'general' | 'health_indicator' | 'pattern'
# - content (text) - Educational content about the marker
# - embedding (vector) - For RAG vector search (pgvector)
# RLS: Public (anyone can read)

# TABLE: audit_log
# - id (uuid, primary key)
# - user_id (uuid, foreign key → users)
# - action (text) - 'upload_report', 'view_analysis', etc.
# - details (jsonb, encrypted) - Any additional context
# - created_at (timestamp)
# RLS: Users see only their own logs
