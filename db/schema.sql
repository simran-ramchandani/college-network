-- ============================================================
--  College Social Network -- Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS college_network;
USE college_network;

-- ── Lookup tables ────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS departments (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS clubs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- ── Core: Person ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS persons (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE,
    year        TINYINT CHECK (year BETWEEN 1 AND 5),
    dept_id     INT,
    role_id     INT,                          -- ← add this
    hostel      VARCHAR(100),
    bio         TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    roles      ENUM('student','alumni','perm_faculty','vis_faculty','nt_faculty','others') NOT NULL,
    FOREIGN KEY (dept_id)  REFERENCES departments(id) ON DELETE SET NULL
);

-- ── Club membership ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS club_memberships (
    person_id   INT,
    club_id     INT,
    role        VARCHAR(50) DEFAULT 'Member',
    member_status ENUM('active', 'passed_out') DEFAULT 'active',
    joined_on   DATE,
    PRIMARY KEY (person_id, club_id),
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE,
    FOREIGN KEY (club_id)   REFERENCES clubs(id)   ON DELETE CASCADE
);

-- ── Courses ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS courses (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    code    VARCHAR(20) NOT NULL UNIQUE,
    name    VARCHAR(150) NOT NULL,
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS course_enrollments (
    person_id   INT,
    course_id   INT,
    semester    VARCHAR(20),
    PRIMARY KEY (person_id, course_id, semester),
    FOREIGN KEY (person_id)  REFERENCES persons(id)  ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE
);

-- ── Relationships (the graph edges) ──────────────────────────

CREATE TABLE IF NOT EXISTS relationships (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    person_a        INT NOT NULL,
    person_b        INT NOT NULL,
    rel_type        ENUM('friend','classmate','project_teammate','mentor','hostel_neighbour','acquaintance','foe','best_friend','alumni','teacher') NOT NULL,
    strength        TINYINT DEFAULT 5 CHECK (strength BETWEEN 1 AND 10),
    since           DATE,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_rel (person_a, person_b, rel_type),
    FOREIGN KEY (person_a) REFERENCES persons(id) ON DELETE CASCADE,
    FOREIGN KEY (person_b) REFERENCES persons(id) ON DELETE CASCADE,
    CHECK (person_a <> person_b)
);

-- ── Events ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS events (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    event_date  DATE,
    location    VARCHAR(150),
    club_id     INT,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS event_attendance (
    person_id   INT,
    event_id    INT,
    PRIMARY KEY (person_id, event_id),
    FOREIGN KEY (person_id) REFERENCES persons(id)  ON DELETE CASCADE,
    FOREIGN KEY (event_id)  REFERENCES events(id)   ON DELETE CASCADE
);

-- ── Useful views ─────────────────────────────────────────────

CREATE OR REPLACE VIEW v_person_connections AS
SELECT
    p1.name  AS person,
    p2.name  AS connected_to,
    r.rel_type,
    r.strength,
    r.since
FROM relationships r
JOIN persons p1 ON r.person_a = p1.id
JOIN persons p2 ON r.person_b = p2.id;

CREATE OR REPLACE VIEW v_person_full AS
SELECT
    p.id, p.name, p.email, p.year,
    d.name  AS department,
    p.hostel, p.bio, p.is_active
FROM persons p
LEFT JOIN departments d ON p.dept_id = d.id;
