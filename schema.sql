PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bubbles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_bubbles (
    user_id INTEGER NOT NULL,
    bubble_id INTEGER NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, bubble_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bubble_id) REFERENCES bubbles(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO bubbles (name, slug, description) VALUES
('Ethereal Nutrition', 'nutrition', 'Practical knowledge for food, meal prep, and everyday nourishment.'),
('Ethereal Era', 'era', 'Ideas, culture, history, society, and technology.'),
('Ethereal Mind', 'mind', 'Learning, cognition, focus, and thoughtful self-development.'),
('Ethereal Finance', 'finance', 'Clear financial literacy and practical money knowledge.'),
('Ethereal Living', 'living', 'Systems, spaces, and knowledge for everyday life.'),
('Ethereal Career', 'career', 'Skills, work, professional growth, and career knowledge.');
