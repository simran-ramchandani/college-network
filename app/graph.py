"""
graph.py — NetworkX graph builder + Pyvis renderer
"""

import networkx as nx
import tempfile
from pathlib import Path
import streamlit.components.v1 as components


# Colour per relationship type
REL_COLOURS = {
    "friend":            "#4CAF50",
    "classmate":         "#2196F3",
    "project_teammate":  "#FF9800",
    "mentor":            "#9C27B0",
    "hostel_neighbour":  "#F44336",
    "acquaintance":      "#9E9E9E",
    "foe":               "#ef4444",
    "best_friend":       "#22c55e",
    "alumni":            "#14b8a6",
    "teacher":           "#a855f7",
}

_graph_editor = components.declare_component(
    "graph_editor",
    path=str(Path(__file__).parent / "components" / "graph_editor"),
)


def build_graph(persons: list, relationships: list) -> nx.Graph:
    G = nx.Graph()
    for p in persons:
        G.add_node(
            p["id"],
            label=p["name"],
            dept=p.get("department", ""),
            year=p.get("year", ""),
            email=p.get("email", ""),
            hostel=p.get("hostel", ""),
            bio=p.get("bio", ""),
            role=p.get("role", ""),
        )
    for r in relationships:
        # find ids from names if needed
        a = r.get("person_a_id") or _name_to_id(persons, r.get("person_a"))
        b = r.get("person_b_id") or _name_to_id(persons, r.get("person_b"))
        if a and b:
            G.add_edge(a, b,
                       rel_type=r["rel_type"],
                       strength=r.get("strength", 5),
                       title=r["rel_type"])
    return G


def _name_to_id(persons, name):
    for p in persons:
        if p["name"] == name:
            return p["id"]
    return None


def render_pyvis(G: nx.Graph, height="600px") -> str:
    """Return path to a temp HTML file with the interactive graph."""
    from pyvis.network import Network

    net = Network(height=height, width="100%", bgcolor="#0e1117",
                  font_color="white", notebook=False)
    net.barnes_hut(gravity=-8000, central_gravity=0.3,
                   spring_length=150, spring_strength=0.05)

    for node_id, data in G.nodes(data=True):
        net.add_node(
            node_id,
            label=data.get("label", str(node_id)),
            title=f"{data.get('label','')} | {data.get('dept','')} | Yr {data.get('year','')}",
            size=18 + G.degree(node_id) * 2,
            color="#00BCD4",
            font={"size": 14, "color": "white"},
        )

    for u, v, data in G.edges(data=True):
        rt = data.get("rel_type", "acquaintance")
        net.add_edge(
            u, v,
            color=REL_COLOURS.get(rt, "#9E9E9E"),
            width=data.get("strength", 5) / 2,
            title=rt,
        )

    # Write to a temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                      dir=tempfile.gettempdir())
    net.save_graph(tmp.name)
    return tmp.name


def render_graph_editor(G: nx.Graph, departments: list[str], rel_types: list[str], key="graph_editor"):
    nodes = []
    edges = []
    positions = nx.spring_layout(
        G,
        seed=7,
        k=2.8 / max(len(G), 1) ** 0.5,
        iterations=120,
        scale=900,
    ) if len(G) else {}

    for node_id, data in G.nodes(data=True):
        x, y = positions.get(node_id, (0, 0))
        nodes.append({
            "id": node_id,
            "label": data.get("label", str(node_id)),
            "title": f"{data.get('label','')} | {data.get('dept','')} | Yr {data.get('year','')}",
            "size": 20 + min(G.degree(node_id), 8) * 2,
            "x": float(x * 1.8),
            "y": float(y * 0.8),
            "profile": {
                "id": node_id,
                "name": data.get("label", str(node_id)),
                "email": data.get("email", ""),
                "department": data.get("dept", ""),
                "year": data.get("year", ""),
                "hostel": data.get("hostel", ""),
                "role": data.get("role", ""),
                "bio": data.get("bio", ""),
            },
        })

    for u, v, data in G.edges(data=True):
        rt = data.get("rel_type", "acquaintance")
        edges.append({
            "from": u,
            "to": v,
            "title": rt,
            "width": data.get("strength", 5) / 2,
            "color": REL_COLOURS.get(rt, "#9E9E9E"),
        })

    return _graph_editor(
        nodes=nodes,
        edges=edges,
        departments=departments,
        relTypes=rel_types,
        default=None,
        key=key,
    )


def get_shortest_path(G: nx.Graph, src_id: int, dst_id: int):
    try:
        path_ids = nx.shortest_path(G, src_id, dst_id)
        return path_ids
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None


def get_centrality(G: nx.Graph) -> dict:
    return nx.degree_centrality(G)


def get_communities(G: nx.Graph):
    from networkx.algorithms.community import greedy_modularity_communities
    return list(greedy_modularity_communities(G))
