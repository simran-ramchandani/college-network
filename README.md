# College Social Network — DBMS Project

A knowledge graph of people you meet in college, built with **MySQL + Python + Streamlit + Pyvis**.

---

## Stack
| Layer        | Tool                     |
|--------------|--------------------------|
| Database     | MySQL                    |
| ORM / Driver | SQLAlchemy + mysql-connector-python |
| UI           | Streamlit                |
| Graph Viz    | NetworkX + Pyvis         |
| Analytics    | Pandas                   |

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up MySQL
```bash
mysql -u root -p < db/schema.sql
mysql -u root -p < db/seed.sql
```

### 3. Configure credentials
Either edit `app/database.py` directly, or set environment variables:
```bash
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=college_network
```

### 4. Run the app
```bash
streamlit run streamlit_app.py
```

---

## Features

### CRUD
- **Create** — Add people, relationships, clubs, memberships
- **Read** — Search people, view connections, browse clubs
- **Update** — Edit person profiles, update relationship type/strength, manage club membership status/since date
- **Delete** — Soft-delete people (mark inactive), recover inactive people, permanently delete people with confirmation, hard-delete relationships

### Graph
- Interactive Pyvis graph — drag nodes, zoom, hover for details
- Node size scales with number of connections
- Edge colour represents relationship type
- Shortest path finder between any two people

### Analytics
- Most connected people (bar chart)
- Relationship type breakdown
- Department statistics
- Common connections between two people

---

## Project Structure
```
college_network/
├── db/
│   ├── schema.sql          # All table definitions + views
│   └── seed.sql            # Sample data (10 people, 14 relationships)
├── app/
│   ├── __init__.py
│   ├── database.py         # SQLAlchemy engine + session
│   ├── crud.py             # All CRUD functions
│   └── graph.py            # NetworkX + Pyvis rendering
├── streamlit_app.py        # Entire UI
├── requirements.txt
└── README.md
```
