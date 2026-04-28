-- ReliefSync-AI Database Schema for Supabase
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/_/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════
-- USERS TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  role TEXT DEFAULT 'citizen' CHECK (role IN ('citizen', 'volunteer', 'ngo_manager', 'government', 'admin')),
  verified BOOLEAN DEFAULT false,
  skills TEXT[],
  phone TEXT,
  location JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- EMERGENCIES TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS emergencies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  category TEXT,
  location JSONB NOT NULL,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'in_progress', 'resolved', 'closed')),
  reported_by UUID REFERENCES users(id) ON DELETE SET NULL,
  affected_count INTEGER DEFAULT 0,
  resources_needed JSONB,
  images TEXT[],
  verified BOOLEAN DEFAULT false,
  ai_severity_score FLOAT,
  ai_priority_score FLOAT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- VOLUNTEERS TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS volunteers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  availability JSONB,
  location JSONB NOT NULL,
  skills TEXT[],
  experience_years INTEGER DEFAULT 0,
  languages TEXT[],
  vehicle_available BOOLEAN DEFAULT false,
  medical_training BOOLEAN DEFAULT false,
  background_verified BOOLEAN DEFAULT false,
  rating FLOAT DEFAULT 0.0,
  tasks_completed INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- TASKS TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  emergency_id UUID REFERENCES emergencies(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'cancelled')),
  priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  required_skills TEXT[],
  location JSONB,
  estimated_duration INTEGER,
  deadline TIMESTAMP WITH TIME ZONE,
  ai_match_score FLOAT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- RESOURCES TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS resources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  category TEXT,
  quantity INTEGER DEFAULT 0,
  unit TEXT,
  location JSONB,
  emergency_id UUID REFERENCES emergencies(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'available' CHECK (status IN ('available', 'allocated', 'depleted')),
  expiry_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- ANALYTICS TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS analytics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type TEXT NOT NULL,
  event_data JSONB,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  emergency_id UUID REFERENCES emergencies(id) ON DELETE SET NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════
-- INDEXES FOR PERFORMANCE
-- ═══════════════════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_emergencies_status ON emergencies(status);
CREATE INDEX IF NOT EXISTS idx_emergencies_severity ON emergencies(severity);
CREATE INDEX IF NOT EXISTS idx_emergencies_created ON emergencies(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_emergency ON tasks(emergency_id);
CREATE INDEX IF NOT EXISTS idx_volunteers_user ON volunteers(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp DESC);

-- ═══════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY (RLS)
-- ═══════════════════════════════════════════════════════════
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE volunteers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- ═══════════════════════════════════════════════════════════
-- RLS POLICIES
-- ═══════════════════════════════════════════════════════════

-- Users: Can read all, update own profile
CREATE POLICY "Users can read all users" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON users FOR INSERT WITH CHECK (auth.uid() = id);

-- Emergencies: Public read, authenticated write
CREATE POLICY "Anyone can read emergencies" ON emergencies FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create emergencies" ON emergencies FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update own emergencies" ON emergencies FOR UPDATE USING (auth.uid() = reported_by);

-- Volunteers: Public read, own update
CREATE POLICY "Anyone can read volunteers" ON volunteers FOR SELECT USING (true);
CREATE POLICY "Users can manage own volunteer profile" ON volunteers FOR ALL USING (auth.uid() = user_id);

-- Tasks: Public read, assigned users can update
CREATE POLICY "Anyone can read tasks" ON tasks FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create tasks" ON tasks FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Assigned users can update tasks" ON tasks FOR UPDATE USING (auth.uid() = assigned_to);

-- Resources: Public read, authenticated write
CREATE POLICY "Anyone can read resources" ON resources FOR SELECT USING (true);
CREATE POLICY "Authenticated users can manage resources" ON resources FOR ALL USING (auth.role() = 'authenticated');

-- Analytics: Service role only
CREATE POLICY "Service role can manage analytics" ON analytics FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- ═══════════════════════════════════════════════════════════
-- FUNCTIONS & TRIGGERS
-- ═══════════════════════════════════════════════════════════

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_emergencies_updated_at BEFORE UPDATE ON emergencies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_volunteers_updated_at BEFORE UPDATE ON volunteers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════
-- SAMPLE DATA (Optional - for testing)
-- ═══════════════════════════════════════════════════════════

-- Insert sample user
INSERT INTO users (id, email, display_name, role, verified, skills)
VALUES 
  ('00000000-0000-0000-0000-000000000001', 'admin@reliefsyncai.com', 'Admin User', 'admin', true, ARRAY['management', 'coordination']),
  ('00000000-0000-0000-0000-000000000002', 'volunteer@reliefsyncai.com', 'Test Volunteer', 'volunteer', true, ARRAY['first_aid', 'rescue'])
ON CONFLICT (id) DO NOTHING;

-- Success message
DO $$
BEGIN
  RAISE NOTICE '✅ ReliefSync-AI database schema created successfully!';
  RAISE NOTICE '📊 Tables: users, emergencies, volunteers, tasks, resources, analytics';
  RAISE NOTICE '🔒 Row Level Security enabled with policies';
  RAISE NOTICE '⚡ Indexes and triggers configured';
END $$;
