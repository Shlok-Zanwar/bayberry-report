
"""Main landing page for Bayberry Data Analytics."""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Bayberry Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.markdown('<div class="main-header">📊 Bayberry Data Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    Welcome to the Bayberry Data Analytics platform!
    
    Use the sidebar to navigate to the following analysis pages:
    """)

    st.markdown("---")

    # Top-level summary cards (static or minimal info)
    st.markdown('<div class="summary-card">🔍 <b>Sales Profit Analysis</b><br>Analyze batch-wise profits, revenue, and cost breakdowns.<br><a href="/Sales_Profit_Analysis" target="_self">Go to Sales Profit Analysis &rarr;</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="summary-card">🔍 <b>Vendor Rate Analysis</b><br>Compare vendor rates for products and identify savings opportunities.<br><a href="/1_%F0%9F%94%8D_Vendor_Analysis" target="_self">Go to Vendor Rate Analysis &rarr;</a></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("Select a page from the sidebar to begin your analysis.")

if __name__ == "__main__":
    main()
