-- 002 — Herkunft von Läufen und Genauigkeit von Citations
--
-- Zwei Ergänzungen, damit historische Peec-Exporte neben eigenen Scrapes
-- liegen können, ohne dass im Dashboard jemand Äpfel mit Birnen vergleicht.

-- Woher stammt der Lauf?
--   searchapi   = eigener Scrape über SearchApi (Ebene 1)
--   peec_import = historischer Export aus dem Peec-Account, importiert
-- Im Dashboard filterbar, damit "unsere" Zeitreihe getrennt auswertbar bleibt.
ALTER TABLE runs ADD COLUMN source TEXT NOT NULL DEFAULT 'searchapi';

CREATE INDEX idx_runs_source ON runs (source);

-- Ist cited_url eine echte URL oder nur eine Domain?
-- Peec exportiert ausschließlich Domains, keine Pfade. Statt URLs zu erfinden,
-- wird das hier ehrlich markiert: url_known = 0 heißt "nur Domain bekannt".
-- Die URL-Ansicht im Dashboard zeigt deshalb nur url_known = 1.
ALTER TABLE citations ADD COLUMN url_known INTEGER NOT NULL DEFAULT 1;

CREATE INDEX idx_citations_url_known ON citations (url_known);
