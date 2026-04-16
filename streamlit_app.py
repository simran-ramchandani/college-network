import pandas as pd
import streamlit as st
from sqlalchemy.exc import IntegrityError

from app import crud, graph as gx
from app.database import SessionLocal, ensure_schema_updates, test_connection


st.set_page_config(
    page_title="College Network",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = ["Graph View", "People", "Relationships", "Clubs", "Analytics", "Settings"]
MEMBER_STATUS_OPTIONS = ["active", "passed_out"]
REL_TYPES = [
    "friend",
    "classmate",
    "project_teammate",
    "mentor",
    "hostel_neighbour",
    "acquaintance",
    "foe",
    "best_friend",
    "alumni",
    "teacher",
]


@st.cache_resource
def get_session():
    return SessionLocal()


def set_page(page_name):
    st.session_state.page = page_name


def refresh_app(message, level="success"):
    st.session_state.flash = {"message": message, "level": level}
    st.rerun()


def show_flash():
    flash = st.session_state.pop("flash", None)
    if flash:
        if hasattr(st, "toast"):
            st.toast(flash["message"])
        else:
            getattr(st, flash["level"])(flash["message"])


def department_maps(db):
    depts = crud.get_all_departments(db)
    return {d["name"]: d["id"] for d in depts}, {d["id"]: d["name"] for d in depts}


db = get_session()
ensure_schema_updates()

if "page" not in st.session_state:
    st.session_state.page = "Graph View"

st.markdown(
    """
    <style>
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    #MainMenu,
    footer {
        display: none !important;
    }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #18181b 0%, #27272a 100%);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #f8fafc;
    }
    [data-testid="stSidebar"] div.stButton > button {
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 8px;
        justify-content: flex-start;
        min-height: 2.75rem;
    }
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: #3b82f6;
        color: #111827;
        border-color: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("College Network")
st.sidebar.caption("Navigate")
for page_name in PAGES:
    st.sidebar.button(
        page_name,
        key=f"nav_{page_name}",
        on_click=set_page,
        args=(page_name,),
        type="primary" if st.session_state.page == page_name else "secondary",
        use_container_width=True,
    )

page = st.session_state.page
show_flash()

if page == "Graph View":
    persons = crud.get_all_persons(db)
    rels = crud.get_all_relationships(db)
    G = gx.build_graph(persons, rels)
    dept_map, _ = department_maps(db)

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stAppViewContainer"] .block-container {
            height: 100vh !important;
            overflow: hidden !important;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlock"],
        div[data-testid="stElementContainer"],
        div[data-testid="stIFrame"] {
            width: 100% !important;
            max-height: 100vh !important;
            overflow: hidden !important;
        }
        iframe {
            display: block;
            width: 100% !important;
            height: 100vh !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    graph_event = gx.render_graph_editor(
        G,
        departments=list(dept_map.keys()),
        rel_types=REL_TYPES,
        key="main_graph_editor",
    )

    if "processed_graph_events" not in st.session_state:
        st.session_state.processed_graph_events = set()

    if graph_event and graph_event.get("requestId") not in st.session_state.processed_graph_events:
        st.session_state.processed_graph_events.add(graph_event["requestId"])

        if graph_event.get("type") == "add_edge":
            try:
                crud.create_relationship(
                    db,
                    graph_event["from"],
                    graph_event["to"],
                    graph_event["relType"],
                    graph_event["strength"],
                    None,
                    graph_event.get("notes", ""),
                )
                refresh_app("Connection added.")
            except IntegrityError:
                db.rollback()
                refresh_app("That connection could not be added. It may already exist.", "error")

        if graph_event.get("type") == "add_person":
            dept_id = dept_map.get(graph_event.get("department"))
            if not graph_event.get("name") or not dept_id:
                refresh_app("That person could not be added. Name and department are required.", "error")
            else:
                try:
                    new_id = crud.create_person(
                        db,
                        graph_event["name"],
                        graph_event.get("email", ""),
                        graph_event.get("year", 1),
                        dept_id,
                        graph_event.get("hostel", ""),
                        graph_event.get("bio", ""),
                        graph_event.get("role", "student"),
                    )
                    refresh_app(f"Added {graph_event['name']} (ID: {new_id}).")
                except IntegrityError:
                    db.rollback()
                    refresh_app("That person could not be added. Check for a duplicate email or missing required field.", "error")

elif page == "People":
    st.title("People")
    tab1, tab2, tab3 = st.tabs(["View / Search", "Add Person", "Edit / Delete"])

    with tab1:
        q = st.text_input("Search by name, email, department, hostel")
        persons = crud.search_persons(db, q) if q else crud.get_all_persons(db)
        st.dataframe(pd.DataFrame(persons), use_container_width=True)

        st.markdown("---")
        st.subheader("View Connections")
        all_persons = crud.get_all_persons(db)
        sel = st.selectbox("Select a person", [p["name"] for p in all_persons])
        if sel:
            pid = next(p["id"] for p in all_persons if p["name"] == sel)
            info = crud.get_person_by_id(db, pid)
            with st.expander(f"Profile: {sel}"):
                st.json(info)
            conns = crud.get_connections_of(db, pid)
            if conns:
                st.dataframe(pd.DataFrame(conns), use_container_width=True)
            else:
                st.info("No connections yet.")

    with tab2:
        st.subheader("Add New Person")
        dept_map, _ = department_maps(db)

        if not dept_map:
            st.info("Add at least one department before adding a person.")
        else:
            with st.form("add_person"):
                name = st.text_input("Full Name *")
                email = st.text_input("Email")
                year = st.selectbox("Year", [1, 2, 3, 4, 5])
                dept = st.selectbox("Department", list(dept_map.keys()))
                hostel = st.text_input("Hostel")
                role = st.selectbox("Role", ["student", "alumni", "perm_faculty", "vis_faculty", "nt_faculty", "others"])
                bio = st.text_area("Bio")
                submitted = st.form_submit_button("+ Add Person")

            if submitted:
                if not name:
                    st.error("Name is required.")
                else:
                    try:
                        new_id = crud.create_person(db, name, email, year, dept_map[dept], hostel, bio, role)
                        st.success(f"Added {name} (ID: {new_id}).")
                    except IntegrityError:
                        db.rollback()
                        st.error("That person could not be added. Check for a duplicate email or missing required field.")

    with tab3:
        st.subheader("Edit or Delete a Person")
        all_persons = crud.get_all_persons(db, include_inactive=True)
        dept_map, _ = department_maps(db)

        person_options = {
            f"{p['name']} [ID {p['id']}] ({'active' if p['is_active'] else 'inactive'})": p
            for p in all_persons
        }
        selected_label = st.selectbox("Select person", list(person_options.keys()), key="edit_sel")

        if selected_label and dept_map:
            p = person_options[selected_label]
            sel_edit = p["name"]
            status_text = "active" if p["is_active"] else "inactive"
            st.caption(f"Current status: {status_text}")
            with st.form("edit_person"):
                name = st.text_input("Name", value=p["name"])
                email = st.text_input("Email", value=p["email"] or "")
                year = st.selectbox("Year", [1, 2, 3, 4, 5], index=(p["year"] or 1) - 1)
                dept = st.selectbox(
                    "Department",
                    list(dept_map.keys()),
                    index=list(dept_map.keys()).index(p["department"]) if p["department"] in dept_map else 0,
                )
                hostel = st.text_input("Hostel", value=p["hostel"] or "")
                bio = st.text_area("Bio", value=p["bio"] or "")
                c1, c2, c3 = st.columns(3)
                save = c1.form_submit_button("Save Changes")
                soft_delete = c2.form_submit_button("Delete (soft)", type="secondary")
                recover = c3.form_submit_button("Recover", type="secondary")

            if save:
                crud.update_person(db, p["id"], name, email, year, dept_map[dept], hostel, bio)
                st.success("Updated.")
            if soft_delete:
                crud.delete_person(db, p["id"])
                st.warning(f"{sel_edit} marked as inactive.")
            if recover:
                crud.recover_person(db, p["id"])
                st.success(f"{sel_edit} recovered.")

            st.markdown("---")
            st.subheader("Permanent Delete")
            st.warning(
                "Permanent delete removes this person from the database and cannot be rolled back. "
                "Related rows may also be removed by foreign-key cascades."
            )
            confirm_permanent = st.checkbox(
                f"I understand that permanently deleting {sel_edit} is final.",
                key=f"confirm_hard_delete_{p['id']}",
            )
            if st.button("Delete Permanently", key=f"hard_delete_{p['id']}", type="primary"):
                if confirm_permanent:
                    crud.hard_delete_person(db, p["id"])
                    refresh_app(f"{sel_edit} permanently deleted.", "warning")
                else:
                    st.error("Please confirm the warning before permanently deleting this record.")
        elif not dept_map:
            st.info("Add at least one department before editing a person.")

elif page == "Relationships":
    st.title("Relationships")
    tab1, tab2, tab3 = st.tabs(["View All", "Add Relationship", "Edit / Delete"])

    with tab1:
        rels = crud.get_all_relationships(db)
        st.dataframe(pd.DataFrame(rels), use_container_width=True)

    with tab2:
        st.subheader("Add New Relationship")
        persons = crud.get_all_persons(db)
        name_map = {p["name"]: p["id"] for p in persons}

        if len(name_map) < 2:
            st.info("Add at least two people before creating a relationship.")
        else:
            with st.form("add_rel"):
                c1, c2 = st.columns(2)
                pa = c1.selectbox("Person A", list(name_map.keys()))
                pb = c2.selectbox("Person B", list(name_map.keys()))
                rt = st.selectbox("Relationship Type", REL_TYPES)
                strength = st.slider("Strength (1-10)", 1, 10, 5)
                since = st.date_input("Since")
                notes = st.text_input("Notes (optional)")
                sub = st.form_submit_button("+ Add Relationship")

            if sub:
                if pa == pb:
                    st.error("A person cannot be connected to themselves.")
                else:
                    try:
                        crud.create_relationship(db, name_map[pa], name_map[pb], rt, strength, since, notes)
                        st.success(f"Added: {pa} to {pb} ({rt}).")
                    except IntegrityError:
                        db.rollback()
                        st.error("That relationship could not be added. It may already exist.")

    with tab3:
        st.subheader("Edit or Delete Relationship")
        rels = crud.get_all_relationships(db)
        if rels:
            options = {f"{r['person_a']} to {r['person_b']} ({r['rel_type']})": r for r in rels}
            sel = st.selectbox("Select", list(options.keys()))
            r = options[sel]

            with st.form("edit_rel"):
                rt = st.selectbox("Type", REL_TYPES, index=REL_TYPES.index(r["rel_type"]) if r["rel_type"] in REL_TYPES else 0)
                strength = st.slider("Strength", 1, 10, int(r["strength"] or 5))
                notes = st.text_input("Notes", value=r["notes"] or "")
                c1, c2 = st.columns(2)
                save = c1.form_submit_button("Save")
                delete = c2.form_submit_button("Delete", type="secondary")

            if save:
                crud.update_relationship(db, r["id"], rt, strength, notes)
                st.success("Updated.")
            if delete:
                crud.delete_relationship(db, r["id"])
                st.warning("Relationship deleted.")
        else:
            st.info("No relationships yet.")

elif page == "Clubs":
    st.title("Clubs")
    tab1, tab2, tab3 = st.tabs(["View Clubs", "Add Club", "Manage Members"])

    with tab1:
        clubs = crud.get_all_clubs(db)
        for club in clubs:
            with st.expander(club["name"]):
                st.write(club.get("description", ""))
                members = crud.get_club_members(db, club["id"])
                if members:
                    st.dataframe(pd.DataFrame(members), use_container_width=True)
                else:
                    st.info("No members yet.")

    with tab2:
        with st.form("add_club"):
            name = st.text_input("Club Name *")
            desc = st.text_area("Description")
            sub = st.form_submit_button("+ Create Club")
        if sub and name:
            crud.create_club(db, name, desc)
            st.success(f"Club '{name}' created.")

    with tab3:
        st.subheader("Add / Remove Member")
        clubs = crud.get_all_clubs(db)
        persons = crud.get_all_persons(db)
        club_map = {c["name"]: c["id"] for c in clubs}
        person_map = {p["name"]: p["id"] for p in persons}

        if club_map and person_map:
            c1, c2 = st.columns(2)
            sel_club = c1.selectbox("Club", list(club_map.keys()))
            sel_person = c2.selectbox("Person", list(person_map.keys()))
            role = st.text_input("Role", value="Member")
            member_status = st.selectbox("Member Status", MEMBER_STATUS_OPTIONS)
            joined_on = st.date_input("Since")

            col1, col2 = st.columns(2)
            if col1.button("+ Add Member"):
                crud.add_club_membership(
                    db,
                    person_map[sel_person],
                    club_map[sel_club],
                    role,
                    member_status,
                    joined_on,
                )
                st.success("Added.")
            if col2.button("Remove Member"):
                crud.remove_club_membership(db, person_map[sel_person], club_map[sel_club])
                st.warning("Removed from club.")
        else:
            st.info("Add at least one club and one person before managing members.")

elif page == "Analytics":
    st.title("Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Most Connected People")
        top = crud.get_most_connected(db, limit=10)
        st.bar_chart(pd.DataFrame(top).set_index("name")["connection_count"])

    with col2:
        st.subheader("Relationship Type Breakdown")
        rt_stats = crud.get_relationship_type_stats(db)
        st.dataframe(pd.DataFrame(rt_stats), use_container_width=True)

    st.markdown("---")
    st.subheader("Department Stats")
    dept_stats = crud.get_dept_stats(db)
    st.dataframe(pd.DataFrame(dept_stats), use_container_width=True)

    st.markdown("---")
    st.subheader("Common Connections Between Two People")
    persons = crud.get_all_persons(db)
    name_map = {p["name"]: p["id"] for p in persons}
    if len(name_map) < 2:
        st.info("Add at least two people to find common connections.")
    else:
        c1, c2 = st.columns(2)
        pa = c1.selectbox("Person A", list(name_map.keys()), key="cc_a")
        pb = c2.selectbox("Person B", list(name_map.keys()), key="cc_b")
        if st.button("Find Common Connections"):
            common = crud.get_common_connections(db, name_map[pa], name_map[pb])
            if common:
                st.success(f"{len(common)} common connection(s):")
                st.dataframe(pd.DataFrame(common), use_container_width=True)
            else:
                st.info("No common connections found.")

elif page == "Settings":
    st.title("Settings")
    st.subheader("Database Connection")
    ok, msg = test_connection()
    if ok:
        st.success(msg)
    else:
        st.error(msg)
        st.info("Update DB_USER, DB_PASSWORD etc. in app/database.py or set environment variables.")

    st.markdown("---")
    st.subheader("Environment Variables")
    st.code(
        """
# Set these before running:
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=college_network
        """,
        language="bash",
    )
