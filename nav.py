import streamlit as st

st.set_page_config(layout="wide")

# ---------- Aggressive CSS to center top nav ----------
st.markdown("""
<style>
/* Target the main header */
header[data-testid="stHeader"] {
    display: flex;
    justify-content: center;
}

/* Target all divs inside header */
header[data-testid="stHeader"] > div {
    display: flex;
    justify-content: center;
    width: 100%;
}

/* Target navigation specifically */
header[data-testid="stHeader"] nav {
    display: flex;
    justify-content: center;
    width: 100%;
}

/* Target the button container */
header[data-testid="stHeader"] nav > div {
    display: flex;
    justify-content: center;
    gap: 1rem;
}

/* Alternative selectors if above doesn't work */
[data-testid="stHeader"] button {
    margin: 0 auto;
}

/* Nuclear option - center everything in header */
header * {
    justify-content: center !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Page functions ----------
def home():
    st.title("Home")
    st.write("Welcome to the app.")

def dashboard():
    st.title("Dashboard")
    st.write("GitHub migration dashboard.")

def editor():
    st.title("Editor")
    st.write("GitHub migration editor.")

# ---------- Create Page objects ----------
home_page = st.Page(home, title="Home")
dashboard_page = st.Page(dashboard, title="Dashboard")
editor_page = st.Page(editor, title="Editor")

# ---------- Sections for grouped top navigation ----------
sections = {
    "Home": [home_page],
    "GitHub migration": [dashboard_page, editor_page],
}

# ---------- Top navigation ----------
pg = st.navigation(sections, position="top")
pg.run()