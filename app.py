"""
GitHub Migration Portal - Main Entry Point
Run this file to start the application: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path

# Set up path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Import base page
from utils.base_page import BasePage

# Setup page
BasePage.setup_page(
    page_title="GitHub Migration Portal",
    page_icon="🏠"
)

# Render header with user menu
BasePage.render_header(
    title="🏠 GitHub Migration Portal",
    show_user_menu=True,
    show_refresh=False
)

st.markdown("---")

# Show login form if needed
BasePage.render_login_form()

# Welcome section
st.header("Welcome to the GitHub Migration Portal")

# Render footer
BasePage.render_footer()