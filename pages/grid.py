import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# --- 1. INITIAL SETUP ---
st.set_page_config(page_title="MySQL Inventory Editor", layout="wide")

if 'master_df' not in st.session_state:
    # Simulating your MySQL data
    st.session_state.master_df = pd.DataFrame({
        'id': range(101, 126),
        'repo_name': [f"service-mesh-{i}" for i in range(25)],
        'status': np.random.choice(['Legacy', 'Verified', 'Migrated'], 25),
        'owner': np.random.choice(['Infra', 'DevOps', 'Security'], 25),
        'last_audit': pd.Timestamp.now().strftime('%Y-%m-%d')
    })

if 'grid_key' not in st.session_state:
    st.session_state.grid_key = 0

def reset_view():
    st.session_state.grid_key += 1

# --- 2. STYLING & JAVASCRIPT ---
# Dynamic Colors for the Status column
cells_style_jscode = JsCode("""
function(params) {
    if (params.value === 'Verified') {
        return {'color': 'white', 'backgroundColor': '#28a745'};
    } else if (params.value === 'Legacy') {
        return {'color': 'white', 'backgroundColor': '#dc3545'};
    } else if (params.value === 'Migrated') {
        return {'color': 'black', 'backgroundColor': '#ffc107'};
    }
}
""")

# Update button - directly triggers update when clicked
update_button_js = JsCode("""
    class UpdateButtonRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #007bff; color: white; border: none;
                border-radius: 4px; padding: 2px 10px; cursor: pointer; font-size: 11px; width: 100%;">
                    Update
                </button>`;
            this.button = this.eGui.querySelector('button');
            this.button.addEventListener('click', () => {
                // First deselect all, then select this row to ensure event fires
                params.api.deselectAll();
                setTimeout(() => {
                    params.node.setSelected(true, true);
                }, 50);
            });
        }
        getGui() { return this.eGui; }
        refresh(params) { return true; }
    }
""")

st.title("🗄️ MySQL Inventory Editor")
st.markdown("Use column headers to **Search/Filter**. Edits are tracked at the bottom.")

@st.fragment
def render_grid():
    """Fragment that only reruns the grid portion, not the whole page."""
    # --- 3. GRID CONFIGURATION ---
    gb = GridOptionsBuilder.from_dataframe(st.session_state.master_df)

    # Default: Every column is searchable via the funnel icon
    gb.configure_default_column(editable=True, filter=True, sortable=True, resizable=True)

    # Specific Column Customization
    gb.configure_column("status", cellStyle=cells_style_jscode)
    gb.configure_column("id", pinned='left', editable=False, cellStyle={'fontWeight': 'bold'})
    gb.configure_column("Update", headerName="Action", cellRenderer=update_button_js, width=90, pinned='right', editable=False)

    # Theme and Zebra Striping
    gb.configure_grid_options(
        rowHeight=35,
        rowSelection='single',
        rowClassRules={'row-grey': 'node.rowIndex % 2 === 0'}
    )
    gb.configure_pagination(paginationPageSize=15)
    gb.configure_side_bar()
    grid_options = gb.build()

    # Action Bar
    col_spacer, col_reset = st.columns([4, 1])
    with col_reset:
        if st.button("🧹 Clear All Filters", use_container_width=True):
            st.session_state.grid_key += 1
            st.rerun(scope="fragment")

    # Render Grid
    grid_response = AgGrid(
        st.session_state.master_df,
        gridOptions=grid_options,
        key=f"inv_grid_{st.session_state.grid_key}",
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        theme='balham',
        height=500,
        custom_css={".row-grey": {"background-color": "#f9f9f9 !important"}}
    )

    # --- HANDLE SINGLE ROW UPDATE (Auto-update on selection) ---
    selected_rows = grid_response.get('selected_rows', None)
    if selected_rows is not None and len(selected_rows) > 0:
        # Get the selected row data
        if isinstance(selected_rows, pd.DataFrame):
            selected_row = selected_rows.iloc[0].to_dict()
        elif isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_row = selected_rows[0]
        else:
            selected_row = None

        if selected_row:
            row_id = selected_row.get('id')

            # Generate a random date within the last 30 days
            random_days = random.randint(1, 30)
            new_date = (datetime.now() - timedelta(days=random_days)).strftime('%Y-%m-%d')

            # Update only this row's last_audit field
            st.session_state.master_df.loc[
                st.session_state.master_df['id'] == row_id, 'last_audit'
            ] = new_date

            st.toast(f"Row {row_id} date updated to {new_date}!", icon="✅")
            st.session_state.grid_key += 1
            st.rerun(scope="fragment")

    return grid_response

# Render the grid fragment
grid_response = render_grid()

# --- 4. DATA SYNC & DIFF LOGIC ---
raw_updated_df = pd.DataFrame(grid_response['data'])

if not raw_updated_df.empty:
    # Safe Column Intersection
    common_cols = [c for c in st.session_state.master_df.columns if c in raw_updated_df.columns]
    updated_df = raw_updated_df[common_cols].copy()

    # Align Data Types
    for col in common_cols:
        updated_df[col] = updated_df[col].astype(st.session_state.master_df[col].dtype)

    # Compare Master vs Updated
    comparison_df = st.session_state.master_df.merge(updated_df, on='id', suffixes=('_old', '_new'))
    
    changed_rows_list = []
    for _, row in comparison_df.iterrows():
        changes = {col: {'old': row[f"{col}_old"], 'new': row[f"{col}_new"]} 
                   for col in common_cols if col != 'id' and row[f"{col}_old"] != row[f"{col}_new"]}
        if changes:
            changed_rows_list.append({'id': row['id'], 'changes': changes})

    # --- 5. REVIEW PANEL ---
    if changed_rows_list:
        st.divider()
        st.subheader(f"📝 Review Pending Updates ({len(changed_rows_list)})")
        
        for item in changed_rows_list:
            with st.container(border=True):
                c_id, c_diff, c_act = st.columns([1, 4, 1])
                c_id.write(f"**ID:** `{item['id']}`")
                with c_diff:
                    # Show exactly what changed in this row
                    for col, vals in item['changes'].items():
                        st.markdown(f"**{col.upper()}**: `{vals['old']}` → :green[**{vals['new']}**]")
                if c_act.button("Discard", key=f"disc_{item['id']}", use_container_width=True):
                    reset_view()

        st.write("##")
        b1, b2 = st.columns([1, 4])
        if b1.button("🚀 Sync to MySQL", type="primary", use_container_width=True):
            st.session_state.master_df = updated_df.copy()
            st.success("Database Synchronized!")
            st.rerun()
        if b2.button("Discard All Edits"):
            reset_view()