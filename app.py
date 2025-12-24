
"""Main landing page for Bayberry Data Analytics."""
import streamlit as st
from src.utils.auth import require_password

# Page configuration
st.set_page_config(
    page_title="Bayberry Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# PASSWORD PROTECTION - Must be first!
# ========================================
require_password()

# ========================================
# APP CONTENT (Only visible after authentication)
# ========================================

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .summary-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">📊 Bayberry Data Analytics</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    st.sidebar.markdown(f"**Logged in as:** {user.get_role_name()}")
    
    st.markdown(f"""
    Welcome to the Bayberry Data Analytics platform!
    
    You are logged in with **{user.get_role_name()}** permissions.
    Use the sidebar to navigate to the following analysis pages:
    """)

    st.markdown("---")

    # Top-level summary cards (filtered by permissions)
    if user.can_access_page("Sales Profit Analysis"):
        st.markdown('<div class="summary-card">💰 <b>Sales Profit Analysis</b><br>Analyze batch-wise profits, revenue, and cost breakdowns.<br><a href="/Sales_Profit_Analysis" target="_self">Go to Sales Profit Analysis &rarr;</a></div>', unsafe_allow_html=True)
    
    if user.can_access_page("Vendor Analysis"):
        st.markdown('<div class="summary-card">🔍 <b>Vendor Rate Analysis</b><br>Compare vendor rates for products and identify savings opportunities.<br><a href="/1_%F0%9F%94%8D_Vendor_Analysis" target="_self">Go to Vendor Rate Analysis &rarr;</a></div>', unsafe_allow_html=True)
    
    if user.can_access_page("Expense Analysis"):
        st.markdown('<div class="summary-card">💳 <b>Expense Analysis</b><br>Track and analyze all business expenses by category and period.<br><a href="/2_%F0%9F%92%B3_Expense_Analysis" target="_self">Go to Expense Analysis &rarr;</a></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("Select a page from the sidebar to begin your analysis.")


if __name__ == "__main__":
    main()
