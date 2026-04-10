"""
crud.py — All Create, Read, Update, Delete operations
Each function takes a SQLAlchemy session and returns plain dicts / lists.
"""

from sqlalchemy import text


# ══════════════════════════════════════════════════════════════
#  PERSONS
# ══════════════════════════════════════════════════════════════

def get_all_persons(db, include_inactive: bool = False):
    where_clause = "" if include_inactive else "WHERE p.is_active = TRUE"
    rows = db.execute(text("""
     SELECT p.id, p.name, p.email, p.year,
         d.name AS department, p.hostel, p.bio, p.roles AS role, p.is_active
        FROM persons p
        LEFT JOIN departments d ON p.dept_id = d.id
        {where_clause}
        ORDER BY p.name
    """.format(where_clause=where_clause))).mappings().all()
    return [dict(r) for r in rows]


def get_person_by_id(db, person_id: int):
    row = db.execute(text("""
        SELECT p.id, p.name, p.email, p.year,
               d.name AS department, p.hostel, p.bio, p.roles AS role, p.is_active
        FROM persons p
        LEFT JOIN departments d ON p.dept_id = d.id
        WHERE p.id = :pid
    """), {"pid": person_id}).mappings().first()
    return dict(row) if row else None


def search_persons(db, query: str):
    q = f"%{query}%"
    rows = db.execute(text("""
        SELECT p.id, p.name, p.email, p.year,
               d.name AS department, p.hostel
        FROM persons p
        LEFT JOIN departments d ON p.dept_id = d.id
        WHERE p.is_active = TRUE
          AND (p.name LIKE :q OR p.email LIKE :q OR d.name LIKE :q OR p.hostel LIKE :q)
        ORDER BY p.name
    """), {"q": q}).mappings().all()
    return [dict(r) for r in rows]


def create_person(db, name, email, year, dept_id, hostel, bio, role="student"):
    db.execute(text("""
        INSERT INTO persons (name, email, year, dept_id, hostel, bio, roles)
        VALUES (:name, :email, :year, :dept_id, :hostel, :bio, :role)
    """), {"name": name, "email": email, "year": year,
           "dept_id": dept_id, "hostel": hostel, "bio": bio, "role": role})
    db.commit()
    row = db.execute(text("SELECT LAST_INSERT_ID() AS id")).mappings().first()
    return row["id"]


def update_person(db, person_id, name, email, year, dept_id, hostel, bio):
    db.execute(text("""
        UPDATE persons
        SET name=:name, email=:email, year=:year,
            dept_id=:dept_id, hostel=:hostel, bio=:bio
        WHERE id=:pid
    """), {"name": name, "email": email, "year": year,
           "dept_id": dept_id, "hostel": hostel, "bio": bio, "pid": person_id})
    db.commit()


def delete_person(db, person_id: int):
    """Soft delete — sets is_active = FALSE."""
    db.execute(text("UPDATE persons SET is_active=FALSE WHERE id=:pid"),
               {"pid": person_id})
    db.commit()


def recover_person(db, person_id: int):
    db.execute(text("UPDATE persons SET is_active=TRUE WHERE id=:pid"),
               {"pid": person_id})
    db.commit()


def hard_delete_person(db, person_id: int):
    db.execute(text("DELETE FROM persons WHERE id=:pid"), {"pid": person_id})
    db.commit()


# ══════════════════════════════════════════════════════════════
#  RELATIONSHIPS
# ══════════════════════════════════════════════════════════════

def get_all_relationships(db):
    rows = db.execute(text("""
        SELECT r.id,
               p1.name AS person_a, p2.name AS person_b,
               r.rel_type, r.strength, r.since, r.notes
        FROM relationships r
        JOIN persons p1 ON r.person_a = p1.id
        JOIN persons p2 ON r.person_b = p2.id
        ORDER BY r.created_at DESC
    """)).mappings().all()
    return [dict(r) for r in rows]


def get_connections_of(db, person_id: int):
    rows = db.execute(text("""
        SELECT p2.id, p2.name, r.rel_type, r.strength, r.since, r.notes
        FROM relationships r
        JOIN persons p2
          ON (r.person_b = p2.id AND r.person_a = :pid)
          OR (r.person_a = p2.id AND r.person_b = :pid)
        WHERE p2.is_active = TRUE
        ORDER BY r.strength DESC
    """), {"pid": person_id}).mappings().all()
    return [dict(r) for r in rows]


def create_relationship(db, person_a, person_b, rel_type, strength, since, notes):
    db.execute(text("""
        INSERT INTO relationships (person_a, person_b, rel_type, strength, since, notes)
        VALUES (:a, :b, :rel_type, :strength, :since, :notes)
    """), {"a": person_a, "b": person_b, "rel_type": rel_type,
           "strength": strength, "since": since, "notes": notes})
    db.commit()


def update_relationship(db, rel_id, rel_type, strength, notes):
    db.execute(text("""
        UPDATE relationships
        SET rel_type=:rel_type, strength=:strength, notes=:notes
        WHERE id=:rid
    """), {"rel_type": rel_type, "strength": strength,
           "notes": notes, "rid": rel_id})
    db.commit()


def delete_relationship(db, rel_id: int):
    db.execute(text("DELETE FROM relationships WHERE id=:rid"), {"rid": rel_id})
    db.commit()


# ══════════════════════════════════════════════════════════════
#  CLUBS
# ══════════════════════════════════════════════════════════════

def get_all_clubs(db):
    rows = db.execute(text("SELECT * FROM clubs ORDER BY name")).mappings().all()
    return [dict(r) for r in rows]


def get_club_members(db, club_id: int):
    rows = db.execute(text("""
        SELECT p.id, p.name, p.year, d.name AS department,
               cm.role, cm.member_status, cm.joined_on AS since
        FROM club_memberships cm
        JOIN persons p ON cm.person_id = p.id
        LEFT JOIN departments d ON p.dept_id = d.id
        WHERE cm.club_id = :cid AND p.is_active = TRUE
        ORDER BY cm.member_status, cm.role, p.name
    """), {"cid": club_id}).mappings().all()
    return [dict(r) for r in rows]


def create_club(db, name, description):
    db.execute(text("INSERT INTO clubs (name, description) VALUES (:name, :desc)"),
               {"name": name, "desc": description})
    db.commit()


def add_club_membership(db, person_id, club_id, role, member_status, joined_on):
    db.execute(text("""
        INSERT INTO club_memberships (person_id, club_id, role, member_status, joined_on)
        VALUES (:pid, :cid, :role, :member_status, :joined_on)
        ON DUPLICATE KEY UPDATE
            role=:role,
            member_status=:member_status,
            joined_on=:joined_on
    """), {
        "pid": person_id,
        "cid": club_id,
        "role": role,
        "member_status": member_status,
        "joined_on": joined_on,
    })
    db.commit()


def remove_club_membership(db, person_id, club_id):
    db.execute(text("""
        DELETE FROM club_memberships WHERE person_id=:pid AND club_id=:cid
    """), {"pid": person_id, "cid": club_id})
    db.commit()


# ══════════════════════════════════════════════════════════════
#  DEPARTMENTS
# ══════════════════════════════════════════════════════════════

def get_all_departments(db):
    rows = db.execute(text("SELECT * FROM departments ORDER BY name")).mappings().all()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════
#  ANALYTICS / ADVANCED READS
# ══════════════════════════════════════════════════════════════

def get_most_connected(db, limit=10):
    rows = db.execute(text("""
        SELECT p.name,
               COUNT(r.id) AS connection_count
        FROM persons p
        LEFT JOIN relationships r
          ON p.id = r.person_a OR p.id = r.person_b
        WHERE p.is_active = TRUE
        GROUP BY p.id, p.name
        ORDER BY connection_count DESC
        LIMIT :lim
    """), {"lim": limit}).mappings().all()
    return [dict(r) for r in rows]


def get_common_connections(db, person_a_id, person_b_id):
    """People who are connected to BOTH person A and person B."""
    rows = db.execute(text("""
        SELECT p.id, p.name
        FROM persons p
        WHERE p.is_active = TRUE
          AND p.id != :a AND p.id != :b
          AND EXISTS (
              SELECT 1 FROM relationships r1
              WHERE (r1.person_a=p.id AND r1.person_b=:a)
                 OR (r1.person_b=p.id AND r1.person_a=:a)
          )
          AND EXISTS (
              SELECT 1 FROM relationships r2
              WHERE (r2.person_a=p.id AND r2.person_b=:b)
                 OR (r2.person_b=p.id AND r2.person_a=:b)
          )
    """), {"a": person_a_id, "b": person_b_id}).mappings().all()
    return [dict(r) for r in rows]


def get_dept_stats(db):
    rows = db.execute(text("""
        SELECT d.name AS department,
               COUNT(p.id) AS total_persons,
               AVG(p.year) AS avg_year
        FROM departments d
        LEFT JOIN persons p ON p.dept_id = d.id AND p.is_active = TRUE
        GROUP BY d.id, d.name
        ORDER BY total_persons DESC
    """)).mappings().all()
    return [dict(r) for r in rows]


def get_relationship_type_stats(db):
    rows = db.execute(text("""
        SELECT rel_type, COUNT(*) AS count,
               ROUND(AVG(strength), 1) AS avg_strength
        FROM relationships
        GROUP BY rel_type
        ORDER BY count DESC
    """)).mappings().all()
    return [dict(r) for r in rows]
