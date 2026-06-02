-- Debates table
CREATE TABLE debates (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  question TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Debate turns table (one row per agent response)
CREATE TABLE debate_turns (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  debate_id UUID REFERENCES debates(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('pro', 'con', 'judge')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security (open policies for MVP — lock down when auth is added)
ALTER TABLE debates ENABLE ROW LEVEL SECURITY;
ALTER TABLE debate_turns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "debates_all" ON debates FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "debate_turns_all" ON debate_turns FOR ALL USING (true) WITH CHECK (true);

-- Enable Supabase Realtime for live frontend updates
ALTER PUBLICATION supabase_realtime ADD TABLE debates;
ALTER PUBLICATION supabase_realtime ADD TABLE debate_turns;
