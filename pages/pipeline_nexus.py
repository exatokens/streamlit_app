import streamlit as st
import streamlit.components.v1 as components
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="Projects Pipelines", layout="wide", page_icon="🔗")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stHeader"] { background: transparent; }

    .nexus-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 55%, #24243e 100%);
        padding: 1.4rem 2rem;
        border-radius: 12px;
        color: white;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 24px rgba(0,0,0,0.35);
    }
    .nexus-header .subtitle {
        font-size: 0.88rem;
        font-weight: 400;
        opacity: 0.5;
        margin-left: 1rem;
    }

    .detail-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 1.1rem;
    }
    .detail-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.74rem;
        font-weight: 700;
        color: white;
    }
    .meta-tag {
        display: inline-block;
        background: #302b63;
        color: #a29bfe;
        border-radius: 5px;
        padding: 1px 8px;
        font-size: 0.74rem;
        font-family: monospace;
    }
    .dep-item {
        border-left: 3px solid #4A3F8F;
        padding: 5px 9px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.82rem;
        background: rgba(74,63,143,0.12);
        line-height: 1.55;
    }
    .prop-row { margin: 6px 0; line-height: 1.5; }
    .prop-label { font-size: 0.7rem; opacity: 0.5; text-transform: uppercase; font-weight: 600; }
    .prop-val   { font-size: 0.88rem; }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        opacity: 0.38;
    }
    .empty-state .icon { font-size: 3.5rem; margin-bottom: 0.6rem; }
    .stale-hint { font-size: 0.78rem; color: #f39c12; margin-top: 0.3rem; }

    /* suppress the agraph iframe's own scrollbar */
    iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── SUPPRESS AGRAPH'S HARDCODED alert() POPUP ──────────────────────────────────
# agraph v0.0.28 has a hardcoded `alert("Clicked node …")` in its React bundle.
# We inject a MutationObserver from a sibling iframe (same-origin) that replaces
# window.alert with a no-op in every iframe it finds, including agraph's.
components.html(
    """
    <script>
    (function () {
        var noop = function () {};
        function suppress(win) {
            try { win.alert = noop; } catch (e) {}
        }
        function watchFrame(el) {
            suppress(el.contentWindow);
            el.addEventListener("load", function () { suppress(el.contentWindow); });
        }
        var par = window.parent;
        par.document.querySelectorAll("iframe").forEach(watchFrame);
        new MutationObserver(function (mutations) {
            mutations.forEach(function (m) {
                m.addedNodes.forEach(function (node) {
                    if (node.tagName === "IFRAME") { watchFrame(node); }
                    if (node.querySelectorAll) {
                        node.querySelectorAll("iframe").forEach(watchFrame);
                    }
                });
            });
        }).observe(par.document.body, { childList: true, subtree: true });
        suppress(par);
    })();
    </script>
    """,
    height=0,
    scrolling=False,
)

# ── SAMPLE DATA ────────────────────────────────────────────────────────────────
SAMPLE_DATA: dict = {
    "metas": [
        {"id": 1, "name": "meta-alpha"},
        {"id": 2, "name": "meta-beta"},
        {"id": 3, "name": "meta-gamma"},
    ],
    "namespaces": [
        {"id": 1, "name": "backend"},
        {"id": 2, "name": "frontend"},
        {"id": 3, "name": "infra"},
    ],
    "projects": [
        {"id": 1, "meta_id": 1, "name": "auth-service",  "namespace_id": 1, "description": "OAuth2 authentication microservice",          "archived": False},
        {"id": 2, "meta_id": 1, "name": "user-api",      "namespace_id": 1, "description": "User management REST API",                    "archived": False},
        {"id": 3, "meta_id": 2, "name": "web-portal",    "namespace_id": 2, "description": "Customer-facing web portal",                  "archived": False},
        {"id": 4, "meta_id": 2, "name": "admin-ui",      "namespace_id": 2, "description": "Internal admin dashboard",                    "archived": False},
        {"id": 5, "meta_id": 3, "name": "k8s-deployer",  "namespace_id": 3, "description": "Kubernetes deployment automation service",    "archived": False},
        {"id": 6, "meta_id": 3, "name": "infra-monitor", "namespace_id": 3, "description": "Infra monitoring and alerting stack",         "archived": True},
    ],
    "pipeline_hosts": [
        {"id": 1, "name": "jenkins-prod", "description": "Production Jenkins instance"},
        {"id": 2, "name": "gitlab-ci",    "description": "GitLab CI/CD runner"},
    ],
    "pipeline_jobs": [
        {"id": 1, "pipeline_host_id": 1, "job_url": "https://jenkins.internal/job/auth-service/build",  "job_name": "auth-svc-build"},
        {"id": 2, "pipeline_host_id": 1, "job_url": "https://jenkins.internal/job/auth-service/deploy", "job_name": "auth-svc-deploy"},
        {"id": 3, "pipeline_host_id": 2, "job_url": "https://gitlab.internal/user-api/pipelines/test",  "job_name": "user-api-test"},
        {"id": 4, "pipeline_host_id": 1, "job_url": "https://jenkins.internal/job/web-portal/build",    "job_name": "web-portal-build"},
        {"id": 5, "pipeline_host_id": 2, "job_url": "https://gitlab.internal/admin-ui/pipelines/lint",  "job_name": "admin-ui-lint"},
        {"id": 6, "pipeline_host_id": 1, "job_url": "https://jenkins.internal/job/k8s-deployer/deploy", "job_name": "k8s-deploy"},
        {"id": 7, "pipeline_host_id": 1, "job_url": "https://jenkins.internal/job/infra-monitor/build", "job_name": "infra-mon-build"},
    ],
    "repository_jobs": [
        {"project_id": 1, "pipeline_job_id": 1, "status": "SUCCESS", "last_run_at": "2026-04-30 10:22", "last_run_by": "alice"},
        {"project_id": 1, "pipeline_job_id": 2, "status": "RUNNING", "last_run_at": "2026-05-01 08:15", "last_run_by": "bob"},
        {"project_id": 2, "pipeline_job_id": 3, "status": "FAILED",  "last_run_at": "2026-04-29 22:00", "last_run_by": "alice"},
        {"project_id": 3, "pipeline_job_id": 4, "status": "SUCCESS", "last_run_at": "2026-04-30 09:00", "last_run_by": "charlie"},
        {"project_id": 4, "pipeline_job_id": 5, "status": "UNKNOWN", "last_run_at": None,               "last_run_by": None},
        {"project_id": 5, "pipeline_job_id": 6, "status": "SUCCESS", "last_run_at": "2026-05-01 07:30", "last_run_by": "dave"},
        {"project_id": 6, "pipeline_job_id": 7, "status": "FAILED",  "last_run_at": "2026-04-28 18:00", "last_run_by": "eve"},
    ],
    "dependencies": [
        {"pipeline_job_id": 2, "dep_vcs_url": "git@gitlab.internal:user-api.git",    "dep_project_id": 2, "checkout_dir": "libs/user-api"},
        {"pipeline_job_id": 4, "dep_vcs_url": "git@gitlab.internal:auth-service.git","dep_project_id": 1, "checkout_dir": "libs/auth"},
        {"pipeline_job_id": 6, "dep_vcs_url": "git@gitlab.internal:auth-service.git","dep_project_id": 1, "checkout_dir": "deps/auth"},
        {"pipeline_job_id": 6, "dep_vcs_url": "git@gitlab.internal:web-portal.git",  "dep_project_id": 3, "checkout_dir": "deps/web-portal"},
    ],
}

# ── VISUAL CONSTANTS ───────────────────────────────────────────────────────────
_META_COLORS = ["#4A90D9", "#9B59B6", "#E67E22"]
_STATUS_COLORS = {
    "SUCCESS": "#27AE60",
    "FAILED":  "#E74C3C",
    "RUNNING": "#2980B9",
    "UNKNOWN": "#7F8C8D",
}
_STATUS_ICONS = {"SUCCESS": "✅", "FAILED": "❌", "RUNNING": "⏳", "UNKNOWN": "❓"}


# ── HELPERS ────────────────────────────────────────────────────────────────────
def _by_id(collection: list, id_val: int) -> dict | None:
    """Return first dict with matching 'id', or None.

    Args:
        collection: List of dicts with an 'id' key.
        id_val: Integer to match.

    Returns:
        Matching dict, or None.
    """
    return next((x for x in collection if x["id"] == id_val), None)


def _meta_color(meta_id: int) -> str:
    """Hex colour for a meta id, cycling through the palette.

    Args:
        meta_id: Integer meta id (1-based).

    Returns:
        Hex colour string.
    """
    return _META_COLORS[(meta_id - 1) % len(_META_COLORS)]


def _status_color(status: str) -> str:
    """Hex colour for a pipeline status string.

    Args:
        status: One of SUCCESS, FAILED, RUNNING, UNKNOWN.

    Returns:
        Hex colour string.
    """
    return _STATUS_COLORS.get(status, "#7F8C8D")


def _assign_positions(
    nodes: list[Node], edges: list[Edge], canvas_w: int, canvas_h: int
) -> None:
    """Assign x/y positions using a left-to-right hierarchical (BFS-layer) layout.

    Each BFS layer from the root is placed in its own vertical column, evenly
    spaced across the canvas width.  Nodes within a column are spread vertically.
    All coordinates are guaranteed to fall within [pad_x, canvas_w-pad_x] ×
    [pad_y, canvas_h-pad_y] so nothing is clipped by the graph viewport.

    Args:
        nodes: List of Node objects to position (first node = root).
        edges: List of Edge objects defining connections.
        canvas_w: Width of the graph canvas in pixels.
        canvas_h: Height of the graph canvas in pixels.
    """
    if not nodes:
        return

    pad_x, pad_y = 110, 70

    # Build adjacency source → {targets}
    adj: dict[str, set[str]] = {}
    for e in edges:
        adj.setdefault(e.source, set()).add(e.target)

    # BFS from root to assign layers
    root_id = nodes[0].id
    layer_of: dict[str, int] = {root_id: 0}
    queue = [root_id]
    while queue:
        nid = queue.pop(0)
        for tgt in adj.get(nid, set()):
            if tgt not in layer_of:
                layer_of[tgt] = layer_of[nid] + 1
                queue.append(tgt)

    # Group node ids by layer in traversal order
    layers: dict[int, list[str]] = {}
    for n in nodes:
        lyr = layer_of.get(n.id, max(layer_of.values(), default=0) + 1)
        layers.setdefault(lyr, []).append(n.id)

    # Column x positions evenly across canvas
    num_layers = max(layers) + 1
    if num_layers == 1:
        col_x = {0: canvas_w / 2}
    else:
        col_x = {
            l: pad_x + l * (canvas_w - 2 * pad_x) / (num_layers - 1)
            for l in range(num_layers)
        }

    # Row y positions within each column
    usable_h = canvas_h - 2 * pad_y
    pos: dict[str, tuple[int, int]] = {}
    for lyr, nids in layers.items():
        x     = col_x.get(lyr, canvas_w - pad_x)
        count = len(nids)
        if count == 1:
            ys = [canvas_h / 2]
        else:
            step = usable_h / (count - 1)
            ys   = [pad_y + i * step for i in range(count)]
        for nid, y in zip(nids, ys):
            pos[nid] = (round(x), round(y))

    # Write positions onto Node objects
    node_lookup = {n.id: n for n in nodes}
    for nid, (x, y) in pos.items():
        if nid in node_lookup:
            node_lookup[nid].x = x
            node_lookup[nid].y = y


# ── GRAPH BUILDER ──────────────────────────────────────────────────────────────
def build_graph(
    project_id: int, data: dict
) -> tuple[list[Node], list[Edge], dict]:
    """Build agraph Node/Edge lists and a node_map for a project's dependency graph.

    Traversal: root project → pipeline jobs → dep projects → their jobs (1 level).

    Node ids are the human-readable names; node_map maps those ids back to
    entity kind and database id so the detail panel can look them up.

    Args:
        project_id: Root project id to expand.
        data: SAMPLE_DATA containing all entity lists.

    Returns:
        Tuple of (nodes, edges, node_map) where node_map is
        {node_id_str: {"kind": "proj"|"job", "entity_id": int}}.
    """
    nodes: list[Node] = []
    edges: list[Edge] = []
    node_map: dict    = {}
    seen_projects: set[int] = set()
    seen_jobs: set[int]     = set()

    def _project_node(proj: dict, is_root: bool = False) -> str:
        """Add project node if unseen; return its node-id string."""
        meta    = _by_id(data["metas"], proj["meta_id"])
        meta_nm = meta["name"] if meta else "unknown"
        node_id = f"{meta_nm}: {proj['name']}"

        if proj["id"] in seen_projects:
            return node_id
        seen_projects.add(proj["id"])

        color = _meta_color(proj["meta_id"])
        node_map[node_id] = {"kind": "proj", "entity_id": proj["id"]}

        nodes.append(Node(
            id=node_id,
            size=550 if is_root else 400,
            color=color,
            symbolType="circle",
            strokeColor="#ffffff",
            renderLabel=True,
            labelPosition="bottom",
        ))
        return node_id

    def _job_node(job: dict, rj: dict | None) -> str:
        """Add pipeline job node if unseen; return its node-id string."""
        if job["id"] in seen_jobs:
            return job["job_name"]
        seen_jobs.add(job["id"])

        status  = rj["status"] if rj else "UNKNOWN"
        color   = _status_color(status)
        node_id = job["job_name"]
        node_map[node_id] = {"kind": "job", "entity_id": job["id"]}

        nodes.append(Node(
            id=node_id,
            size=300,
            color=color,
            symbolType="circle",
            strokeColor="#e0e0e0",
            renderLabel=True,
            labelPosition="bottom",
        ))
        return node_id

    def _edge(src: str, tgt: str, color: str, width: float = 2.0,
              dashed: bool = False) -> None:
        """Append an unlabelled edge."""
        e = Edge(
            source=src,
            target=tgt,
            color=color,
            strokeWidth=width,
            renderLabel=False,
            type="CURVE_SMOOTH",
        )
        if dashed:
            e.strokeDasharray = "6,3"
        edges.append(e)

    root = _by_id(data["projects"], project_id)
    if not root:
        return nodes, edges, node_map

    root_nid = _project_node(root, is_root=True)
    root_rjs = [rj for rj in data["repository_jobs"] if rj["project_id"] == project_id]

    for rj in root_rjs:
        job = _by_id(data["pipeline_jobs"], rj["pipeline_job_id"])
        if not job:
            continue

        job_nid = _job_node(job, rj)
        _edge(root_nid, job_nid, "#8e9eb5", width=2.5)

        for dep in [d for d in data["dependencies"] if d["pipeline_job_id"] == job["id"]]:
            dep_pid = dep.get("dep_project_id")
            if not dep_pid:
                continue
            dep_proj = _by_id(data["projects"], dep_pid)
            if not dep_proj:
                continue

            dep_nid = _project_node(dep_proj, is_root=False)
            _edge(job_nid, dep_nid, "#E67E22", width=1.8, dashed=True)

            for drj in [r for r in data["repository_jobs"] if r["project_id"] == dep_pid]:
                dep_job = _by_id(data["pipeline_jobs"], drj["pipeline_job_id"])
                if not dep_job:
                    continue
                dep_job_nid = _job_node(dep_job, drj)
                _edge(dep_nid, dep_job_nid, "#8e9eb5", width=1.5)

    _assign_positions(nodes, edges, canvas_w=860, canvas_h=560)
    return nodes, edges, node_map


# ── NODE DETAIL RENDERER ───────────────────────────────────────────────────────
def render_node_detail(node_id: str, data: dict, node_map: dict) -> None:
    """Render rich detail card for a clicked graph node.

    Args:
        node_id: Clicked node id string returned by agraph().
        data: Full SAMPLE_DATA dict.
        node_map: {node_id: {"kind": "proj"|"job", "entity_id": int}}.
    """
    info = node_map.get(node_id)
    if not info:
        st.warning(f"Unknown node: `{node_id}`")
        return

    def _prop(label: str, value: str) -> str:
        return (
            f"<div class='prop-row'>"
            f"<div class='prop-label'>{label}</div>"
            f"<div class='prop-val'>{value}</div>"
            f"</div>"
        )

    if info["kind"] == "proj":
        proj  = _by_id(data["projects"], info["entity_id"])
        if not proj:
            st.warning("Project data not found.")
            return
        meta  = _by_id(data["metas"], proj["meta_id"])
        ns    = _by_id(data["namespaces"], proj["namespace_id"])
        color = _meta_color(proj["meta_id"])
        rjs   = [rj for rj in data["repository_jobs"] if rj["project_id"] == proj["id"]]

        arc_html = (
            "&nbsp;<span style='background:#c0392b;border-radius:4px;"
            "padding:1px 6px;font-size:0.68rem;color:white'>archived</span>"
            if proj["archived"] else ""
        )
        body = (
            f"<div class='detail-card'>"
            f"<div class='detail-title'>📁 {proj['name']}{arc_html}</div>"
            f"<span class='meta-tag' style='border-left:3px solid {color}'>{meta['name'] if meta else '—'}</span>"
            f"<hr style='border-color:rgba(255,255,255,0.07);margin:10px 0'>"
            + _prop("Namespace", ns["name"] if ns else "—")
            + _prop("Description", f"<span style='opacity:.75'>{proj.get('description','—')}</span>")
            + _prop("Pipeline jobs", f"<span style='font-size:1.5rem;font-weight:800;color:{color}'>{len(rjs)}</span>")
            + "</div>"
        )
        st.markdown(body, unsafe_allow_html=True)

        if rjs:
            st.markdown("**Job statuses:**")
            for rj in rjs:
                job  = _by_id(data["pipeline_jobs"], rj["pipeline_job_id"])
                if not job:
                    continue
                sc   = _status_color(rj["status"])
                icon = _STATUS_ICONS.get(rj["status"], "❓")
                st.markdown(
                    f"<div class='dep-item'>{icon}&nbsp;"
                    f"<b>{job['job_name']}</b>&nbsp;"
                    f"<span class='badge' style='background:{sc}'>{rj['status']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    elif info["kind"] == "job":
        job   = _by_id(data["pipeline_jobs"], info["entity_id"])
        if not job:
            st.warning("Job data not found.")
            return
        host  = _by_id(data["pipeline_hosts"], job["pipeline_host_id"])
        rj    = next((r for r in data["repository_jobs"] if r["pipeline_job_id"] == job["id"]), None)
        status = rj["status"] if rj else "UNKNOWN"
        sc     = _status_color(status)
        icon   = _STATUS_ICONS.get(status, "❓")
        deps   = [d for d in data["dependencies"] if d["pipeline_job_id"] == job["id"]]

        body = (
            f"<div class='detail-card'>"
            f"<div class='detail-title'>⚙️ {job['job_name']}</div>"
            f"<span class='badge' style='background:{sc}'>{icon} {status}</span>"
            f"<hr style='border-color:rgba(255,255,255,0.07);margin:10px 0'>"
            + _prop("Host", f"<code style='font-size:.8rem'>{host['name'] if host else '—'}</code>")
            + _prop("Job URL", f"<span style='font-size:.72rem;opacity:.6;word-break:break-all'>{job['job_url']}</span>")
            + _prop("Last run", rj["last_run_at"] if rj and rj["last_run_at"] else "—")
            + _prop("Triggered by", rj["last_run_by"] if rj and rj["last_run_by"] else "—")
            + "</div>"
        )
        st.markdown(body, unsafe_allow_html=True)

        st.markdown(f"**Upstream dependencies** ({len(deps)}):")
        if deps:
            for dep in deps:
                dep_proj  = _by_id(data["projects"], dep.get("dep_project_id"))
                proj_name = dep_proj["name"] if dep_proj else "external"
                st.markdown(
                    f"<div class='dep-item'>"
                    f"🔗 <b>{proj_name}</b><br>"
                    f"<span style='opacity:.5;font-size:.72rem'>{dep['dep_vcs_url']}</span><br>"
                    f"<span style='opacity:.45;font-size:.7rem'>→ {dep['checkout_dir']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<span style='opacity:.4;font-size:.82rem'>No upstream dependencies.</span>",
                unsafe_allow_html=True,
            )


# ── SESSION STATE ──────────────────────────────────────────────────────────────
for _k, _v in {
    "pn_selected_node":    None,
    "pn_graph_generated":  False,
    "pn_graph_project_id": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Purge stale keys from previous versions of this page
for _stale in ("pn_node_map", "pn_nodes", "pn_edges"):
    st.session_state.pop(_stale, None)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="nexus-header">🔗 Projects Pipelines'
    '<span class="subtitle">CI/CD Dependency Explorer</span></div>',
    unsafe_allow_html=True,
)

# ── CONTROLS ───────────────────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])

with ctrl1:
    meta_map = {m["name"]: m["id"] for m in SAMPLE_DATA["metas"]}
    selected_meta_name = st.selectbox(
        "Meta",
        options=["— select —"] + list(meta_map.keys()),
        help="Start typing to filter",
    )
    selected_meta_id = meta_map.get(selected_meta_name)

with ctrl2:
    if selected_meta_id:
        proj_map = {
            p["name"]: p["id"]
            for p in SAMPLE_DATA["projects"]
            if p["meta_id"] == selected_meta_id
        }
        selected_proj_name = st.selectbox(
            "Project",
            options=["— select —"] + list(proj_map.keys()),
            help="Projects in selected meta",
        )
        selected_proj_id = proj_map.get(selected_proj_name)
    else:
        st.selectbox("Project", options=["— select meta first —"], disabled=True)
        selected_proj_id = None

with ctrl3:
    st.write("")
    st.write("")
    generate_clicked = st.button(
        "Generate Graph",
        type="primary",
        use_container_width=True,
        disabled=not selected_proj_id,
    )

if generate_clicked and selected_proj_id:
    st.session_state.pn_graph_generated  = True
    st.session_state.pn_graph_project_id = selected_proj_id
    st.session_state.pn_selected_node    = None

is_stale = (
    st.session_state.pn_graph_generated
    and selected_proj_id
    and selected_proj_id != st.session_state.pn_graph_project_id
)
if is_stale:
    st.markdown(
        "<div class='stale-hint'>⚠ Selection changed — click Generate to refresh.</div>",
        unsafe_allow_html=True,
    )

# ── SIDEBAR: minimal navigation ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔗 Projects Pipelines")

# ── MAIN CANVAS ────────────────────────────────────────────────────────────────
if st.session_state.pn_graph_generated:
    # Rebuild graph fresh on every render — ensures the JSON sent to the agraph
    # component is always identical (deterministic build), preventing the
    # component from re-initialising and losing the clicked-node return value.
    nodes, edges, node_map = build_graph(
        st.session_state.pn_graph_project_id, SAMPLE_DATA
    )

    graph_col, detail_col = st.columns([3, 1])

    with graph_col:
        config = Config(
            width=860,
            height=560,
            directed=False,
            nodeHighlightBehavior=True,
            highlightColor="#F1C40F",
            collapsible=False,
        )
        config.staticGraphWithDragAndDrop = True

        clicked = agraph(nodes=nodes, edges=edges, config=config)

        # Use `is not None` so a falsy node-id string still registers
        if clicked is not None:
            st.session_state.pn_selected_node = clicked

    with detail_col:
        st.markdown("#### Node Details")
        selected = st.session_state.pn_selected_node

        if selected:
            if selected in node_map:
                render_node_detail(selected, SAMPLE_DATA, node_map)
            else:
                # Node id returned by agraph doesn't match current graph —
                # happens when the user switches project without clearing state.
                st.info(f"Node **{selected}** is not in the current graph. "
                        "Click a visible node to inspect it.")
        else:
            st.markdown(
                "<div class='detail-card' style='text-align:center;"
                "padding:2.5rem 1rem;opacity:.38'>"
                "<div style='font-size:2rem'>👆</div>"
                "<p style='margin:0'>Click any node<br>to see details</p>"
                "</div>",
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        "<div class='empty-state'>"
        "<div class='icon'>🔗</div>"
        "<p>Select a <b>meta</b> and <b>project</b>, then click <b>Generate Graph</b></p>"
        "</div>",
        unsafe_allow_html=True,
    )
