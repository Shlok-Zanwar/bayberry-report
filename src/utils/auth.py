"""Shared authentication module for all Streamlit pages."""
import streamlit as st


def require_password():
    """Require password authentication before showing any app content.
    
    This function should be called at the top of every page before any
    data loading, processing, or UI rendering occurs.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("### 🔒 Bayberry Data Analytics - Login Required")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")
        st.stop()
