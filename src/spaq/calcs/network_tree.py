
from collections import defaultdict, deque
from typing import Dict, Tuple, Set, List
import pandas as pd
from .network import dp_darcy_weissbach, dp_minors

def build_graph(edges_df: pd.DataFrame):
    G = defaultdict(list)
    indeg = defaultdict(int)
    nodes = set()
    for r in edges_df.itertuples(index=False):
        u = str(getattr(r, 'from_node'))
        v = str(getattr(r, 'to_node'))
        G[u].append(v)
        indeg[v] += 1
        nodes.add(u); nodes.add(v)
    return G, indeg, nodes

def topo_order(G, indeg):
    indeg_copy = dict(indeg)
    all_nodes = set(list(G.keys()) + list(indeg_copy.keys()))
    q = deque([n for n in all_nodes if indeg_copy.get(n,0)==0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in G.get(u, []):
            indeg_copy[v] = indeg_copy.get(v,0) - 1
            if indeg_copy[v] == 0:
                q.append(v)
    return order

def demands_by_node(nodes_df: pd.DataFrame) -> Dict[str, float]:
    d = {}
    for r in nodes_df.itertuples(index=False):
        d[str(getattr(r,'node_id'))] = float(getattr(r,'demand_lpm'))
    return d

def compute_edge_flows(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> Dict[Tuple[str,str], float]:
    G, indeg, nodes = build_graph(edges_df)
    demands = demands_by_node(nodes_df)
    order = topo_order(G, indeg)
    subtree = {n: float(demands.get(n,0.0)) for n in nodes}
    for u in reversed(order):
        for v in G.get(u, []):
            subtree[u] = subtree.get(u, 0.0) + subtree.get(v, 0.0)
    flows = {}
    for r in edges_df.itertuples(index=False):
        u = str(getattr(r,'from_node')); v = str(getattr(r,'to_node'))
        flows[(u,v)] = float(subtree.get(v,0.0))
    return flows

def compute_dp_on_edges(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, temp_C: float = 40.0):
    flows = compute_edge_flows(nodes_df, edges_df)
    rows = []
    for r in edges_df.itertuples(index=False):
        u = str(getattr(r,'from_node')); v = str(getattr(r,'to_node'))
        Q = float(flows[(u,v)])
        L = float(getattr(r,'comprimento_m')); Dmm = float(getattr(r,'diametro_mm')); mat = str(getattr(r,'material')); K = float(getattr(r,'K_local'))
        dp_fric_kpa, dbg = dp_darcy_weissbach(Q, L, Dmm, material=mat, temp_C=temp_C)
        dp_loc_kpa = dp_minors(Q, Dmm, K, temp_C=temp_C)
        dp_edge = dp_fric_kpa + dp_loc_kpa
        rows.append({
            "from": u, "to": v, "Q_lpm": Q, "Δp_fric_kPa": dp_fric_kpa, "Δp_local_kPa": dp_loc_kpa, "Δp_total_kPa": dp_edge,
            "Re": dbg["Re"], "f": dbg["f"], "v_m_s": dbg["v"]
        })
    edge_df = pd.DataFrame(rows)
    return edge_df, flows

def path_dp_to_sinks(edge_df: pd.DataFrame, nodes_df: pd.DataFrame, edges_df: pd.DataFrame):
    dp_map = {(r["from"], r["to"]): float(r["Δp_total_kPa"]) for _, r in edge_df.iterrows()}
    G, indeg, nodes = build_graph(edges_df)
    sinks = [n for n in nodes if n not in G or len(G[n])==0]
    parent = {}
    for r in edges_df.itertuples(index=False):
        u = str(getattr(r,'from_node')); v = str(getattr(r,'to_node'))
        parent[v] = u
    sink_rows = []
    for s in sinks:
        dp = 0.0
        cur = s
        path = []
        while cur in parent:
            p = parent[cur]
            dp += dp_map.get((p,cur), 0.0)
            path.append((p,cur))
            cur = p
        sink_rows.append({"sink": s, "Δp_path_kPa": dp, "edges": path[::-1]})
    return sink_rows
