CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  occurred_at INTEGER NOT NULL,
  received_at INTEGER NOT NULL,
  visitor_key TEXT NOT NULL,
  session_key TEXT NOT NULL,
  series_key TEXT NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('view','missing')),
  menu TEXT NOT NULL,
  region TEXT NOT NULL,
  product_id TEXT NOT NULL,
  product_label TEXT NOT NULL,
  model_id TEXT NOT NULL,
  model_label TEXT NOT NULL,
  run_utc TEXT NOT NULL,
  forecast_hour REAL,
  valid_utc TEXT NOT NULL,
  detail_token TEXT NOT NULL,
  view_context TEXT NOT NULL CHECK(view_context IN ('single','compare')),
  image_source TEXT NOT NULL,
  loaded_count INTEGER NOT NULL,
  expected_count INTEGER NOT NULL,
  load_ms INTEGER,
  device_class TEXT NOT NULL CHECK(device_class IN ('desktop','mobile','tablet'))
);
CREATE INDEX IF NOT EXISTS events_time ON events(occurred_at);
CREATE INDEX IF NOT EXISTS events_visitor_time ON events(visitor_key,occurred_at DESC,event_id);
CREATE INDEX IF NOT EXISTS events_scope ON events(outcome,occurred_at,visitor_key,series_key);
