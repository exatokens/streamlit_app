import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Migration Command Center", layout="wide")

# Initialize State
for key, default in {
    'stage': 0, 
    'selected_repo': None, 
    'is_migrating': False,
    'log_history': []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- 2. DYNAMIC STATUS LOGIC ---
def get_step_meta(step_index, title, current_stage, is_migrating):
    """Generates titles and icons to act as manual status indicators"""
    if current_stage > step_index:
        return f"{title} (Completed)", "check-circle-fill"
    if current_stage == step_index:
        if is_migrating:
            return f"{title} (Running...)", "loading"
        return f"{title} (Active)", "play-circle-fill"
    return f"{title} (Pending)", "circle"

# --- 3. TOP NAVIGATION (VISUAL ONLY) ---
st.title("🚀 Infrastructure Automation Portal")

# We build the items dynamically. Since we aren't using a 'key' or 
# capturing the output, clicking them won't trigger any state changes.
step_items = [
    sac.StepsItem(title=get_step_meta(0, "Select", st.session_state.stage, False)[0], 
                  icon=get_step_meta(0, "Select", st.session_state.stage, False)[1]),
    sac.StepsItem(title=get_step_meta(1, "Verify", st.session_state.stage, False)[0], 
                  icon=get_step_meta(1, "Verify", st.session_state.stage, False)[1]),
    sac.StepsItem(title=get_step_meta(2, "Migrate", st.session_state.stage, st.session_state.is_migrating)[0], 
                  icon=get_step_meta(2, "Migrate", st.session_state.stage, st.session_state.is_migrating)[1]),
    sac.StepsItem(title=get_step_meta(3, "Finish", st.session_state.stage, False)[0], 
                  icon=get_step_meta(3, "Finish", st.session_state.stage, False)[1]),
]

sac.steps(items=step_items, index=st.session_state.stage, size='small')
st.divider()

# --- 4. MAIN LAYOUT ---
col_main, col_sidebar = st.columns([3, 1])

with col_main:
    # --- STAGE 0: SELECTION ---
    if st.session_state.stage == 0:
        st.subheader("Step 1: Resource Discovery")
        st.write("Identify the Bitbucket repository intended for GitHub migration.")
        repo = st.selectbox("Select Target", ["auth-service", "data-api", "web-portal"], index=None)
        st.session_state.selected_repo = repo

    # --- STAGE 1: VERIFICATION ---
    elif st.session_state.stage == 1:
        st.subheader("Step 2: Pre-Flight Verification")
        
        st.info(f"Targeting: **{st.session_state.selected_repo}**")
        st.success("Repository accessibility confirmed. SSH handshake successful.")
        st.graphviz_chart(f'digraph {{ rankdir=LR; "Bitbucket" -> "Validation" -> "Ready"; }}')

    # --- STAGE 2: EXECUTION ---
    elif st.session_state.stage == 2:
        st.subheader("Step 3: Migration Execution")
        with st.status("Triggering Jenkins Pipeline...", expanded=True) as status:
            st.write("Initializing secure tunnel...")
            st.write("Mirroring git objects (this may take 30 mins)...")
            # Mimic Jenkins callback
            if st.button("Simulate Jenkins Completion"):
                st.session_state.is_migrating = False
                st.session_state.stage = 3
                st.rerun()

    # --- STAGE 3: FINISH ---
    elif st.session_state.stage == 3:
        st.balloons()
        st.success(f"✅ Migration of **{st.session_state.selected_repo}** is complete!")
        st.markdown("All git history, branches, and tags have been pushed to GitHub Enterprise.")

with col_sidebar:
    st.write("### 🛠 Actions")
    with st.container(border=True):
        st.write(f"**Target:** `{st.session_state.selected_repo or 'None'}`")
        
        # Navigation logic controlled ONLY by buttons
        if st.session_state.stage == 0:
            if st.button("Next: Verify →", use_container_width=True, disabled=not st.session_state.selected_repo):
                st.session_state.stage = 1
                st.rerun()
        
        elif st.session_state.stage == 1:
            if st.button("🚀 Start Migration", type="primary", use_container_width=True):
                st.session_state.is_migrating = True
                st.session_state.stage = 2
                st.rerun()
            if st.button("← Back", use_container_width=True):
                st.session_state.stage = 0
                st.rerun()

        elif st.session_state.stage == 3:
            if st.button("Start New Job", use_container_width=True):
                st.session_state.stage = 0
                st.session_state.selected_repo = None
                st.rerun()

# --- 5. HISTORY TABLE ---
st.write("---")
st.subheader("📜 Recent Activity")
history_data = {
    "Timestamp": ["2026-01-20 14:30", "2026-01-20 16:15"],
    "Repo": ["auth-service", "legacy-db"],
    "Result": ["Completed", "Completed"]
}
st.table(pd.DataFrame(history_data))