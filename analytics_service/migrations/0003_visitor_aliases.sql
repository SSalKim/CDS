CREATE TABLE IF NOT EXISTS visitor_aliases (
  visitor_key TEXT PRIMARY KEY,
  nickname TEXT NOT NULL,
  updated_at INTEGER NOT NULL
);
