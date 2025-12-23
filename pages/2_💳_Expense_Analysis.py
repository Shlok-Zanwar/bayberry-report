"""Expense Analysis Dashboard."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

from src.utils.auth import require_password
from src.services.expense_reader import ExpenseReaderService
from src.services.expense_analysis import ExpenseAnalysisService

# Page configuration
st.set_page_config(
    page_title="Expense Analysis",
    page_icon="💳",
    layout="wide",
)

# ========================================
# PASSWORD PROTECTION - Must be first!
# ========================================
require_password()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_expense_data():
    """Load and transform expense data."""
    expense_file = Path('BayberryExpenses.xlsx')
    
    if not expense_file.exists():
        st.error(f"❌ Expense file not found: {expense_file}")
        st.stop()
    
    reader = ExpenseReaderService(str(expense_file))
    expenses = reader.transform_expenses()
    
    return expenses


@st.cache_data
def get_analysis(_expenses):
    """Get expense analysis (cached)."""
    analysis = ExpenseAnalysisService(_expenses)
    return analysis


def format_currency(amount):
    """Format amount as Indian currency."""
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.2f}Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.2f}L"
    else:
        return f"₹{amount:,.2f}"


def main():
    """Main expense analysis dashboard."""
    
    # Header
    st.markdown('<div class="main-header">💳 Expense Analysis Dashboard</div>', unsafe_allow_html=True)
    st.markdown("**Track and analyze all business expenses**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading expense data..."):
        all_expenses = load_expense_data()
        analysis_service = get_analysis(all_expenses)
    
    # Get summary stats
    summary = analysis_service.get_summary_stats()
    
    # ============================================
    # SUMMARY STATISTICS (TOP SECTION)
    # ============================================
    st.header("📊 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Debit (Expenses)",
            value=format_currency(summary['total_debit']),
            help="Total expense amount (Dr)"
        )
    
    with col2:
        st.metric(
            label="Total Credit (Refunds)",
            value=format_currency(summary['total_credit']),
            help="Total credit/refund amount (Cr)"
        )
    
    with col3:
        st.metric(
            label="Net Expense",
            value=format_currency(summary['net_expense']),
            delta=f"-{format_currency(summary['total_credit'])}",
            help="Total Debit - Total Credit"
        )
    
    with col4:
        st.metric(
            label="Total Transactions",
            value=f"{summary['total_transactions']:,}",
            help="Total number of expense records"
        )
    
    with col5:
        st.metric(
            label="Avg Expense/Txn",
            value=format_currency(summary['avg_expense']),
            help="Average expense per transaction"
        )
    
    # Date range
    st.info(f"📅 Data Period: **{summary['date_range']['start']}** to **{summary['date_range']['end']}**")
    
    st.markdown("---")
    
    # ============================================
    # FILTERS SECTION
    # ============================================
    st.header("🎯 Filters")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        # Date range filter
        min_date = datetime.strptime(summary['date_range']['start'], '%Y-%m-%d').date()
        max_date = datetime.strptime(summary['date_range']['end'], '%Y-%m-%d').date()
        
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter by date range"
        )
    
    with filter_col2:
        # Group filter
        all_groups = sorted(list(set(e.group for e in all_expenses)))
        selected_groups = st.multiselect(
            "Expense Group",
            options=all_groups,
            default=all_groups,
            help="Filter by expense group (Direct/Indirect)"
        )
    
    with filter_col3:
        # Category filter
        all_categories = sorted(list(set(e.category for e in all_expenses)))
        selected_categories = st.multiselect(
            "Category",
            options=all_categories,
            default=all_categories,
            help="Filter by business category"
        )
    
    with filter_col4:
        # Particular search
        search_term = st.text_input(
            "Search Particulars",
            placeholder="Enter keyword...",
            help="Search in expense particulars"
        )
    
    # Apply filters
    filtered_expenses = all_expenses
    
    # Date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_expenses = [
            e for e in filtered_expenses
            if e.date and start_date <= e.date.date() <= end_date
        ]
    
    # Group filter
    if selected_groups:
        filtered_expenses = [e for e in filtered_expenses if e.group in selected_groups]
    
    # Category filter
    if selected_categories:
        filtered_expenses = [e for e in filtered_expenses if e.category in selected_categories]
    
    # Search filter
    if search_term:
        filtered_expenses = [
            e for e in filtered_expenses
            if search_term.lower() in e.particulars.lower()
        ]
    
    st.info(f"📊 Showing **{len(filtered_expenses):,}** of **{len(all_expenses):,}** transactions")
    
    st.markdown("---")
    
    # ============================================
    # EXPENSE TABLE
    # ============================================
    st.header("📋 Expense Records")
    
    if filtered_expenses:
        # Create filtered analysis
        filtered_analysis = ExpenseAnalysisService(filtered_expenses)
        expenses_df = filtered_analysis.create_expense_dataframe()
        
        # Format the dataframe for display
        display_df = expenses_df.copy()
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        display_df['Debit'] = display_df['Debit'].apply(lambda x: f"₹{x:,.2f}" if x > 0 else "")
        display_df['Credit'] = display_df['Credit'].apply(lambda x: f"₹{x:,.2f}" if x > 0 else "")
        display_df['Net Amount'] = display_df['Net Amount'].apply(lambda x: f"₹{x:,.2f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Download button
        csv = expenses_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"expense_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No expenses found matching the filters.")
    
    st.markdown("---")
    
    # ============================================
    # INSIGHTS & ANALYTICS
    # ============================================
    
    if filtered_expenses:
        filtered_analysis = ExpenseAnalysisService(filtered_expenses)
        
        # GROUP ANALYSIS
        st.markdown('<div class="section-header">🏢 Expense by Group (Direct vs Indirect)</div>', unsafe_allow_html=True)
        
        group_summary = filtered_analysis.get_group_summary()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Group summary table
            group_df = pd.DataFrame([
                {
                    'Group': group,
                    'Transactions': data['count'],
                    'Total Debit': f"₹{data['total_debit']:,.2f}",
                    'Total Credit': f"₹{data['total_credit']:,.2f}",
                    'Net Expense': f"₹{data['net_expense']:,.2f}",
                }
                for group, data in group_summary.items()
            ])
            st.dataframe(group_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Pie chart for group distribution
            group_chart_data = pd.DataFrame([
                {'Group': group, 'Net Expense': data['net_expense']}
                for group, data in group_summary.items()
            ])
            
            if not group_chart_data.empty:
                fig = px.pie(
                    group_chart_data,
                    values='Net Expense',
                    names='Group',
                    title='Net Expense Distribution by Group',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # CATEGORY ANALYSIS
        st.markdown('<div class="section-header">📂 Expense by Category</div>', unsafe_allow_html=True)
        
        category_summary = filtered_analysis.get_category_summary()
        
        # Sort by net expense
        sorted_categories = sorted(category_summary.items(), key=lambda x: x[1]['net_expense'], reverse=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Category summary table
            category_df = pd.DataFrame([
                {
                    'Category': category,
                    'Transactions': data['count'],
                    'Total Debit': f"₹{data['total_debit']:,.2f}",
                    'Total Credit': f"₹{data['total_credit']:,.2f}",
                    'Net Expense': f"₹{data['net_expense']:,.2f}",
                }
                for category, data in sorted_categories
            ])
            st.dataframe(category_df, use_container_width=True, hide_index=True, height=400)
        
        with col2:
            # Bar chart for category expenses
            category_chart_data = pd.DataFrame([
                {'Category': category, 'Net Expense': data['net_expense']}
                for category, data in sorted_categories[:10]  # Top 10
            ])
            
            if not category_chart_data.empty:
                fig = px.bar(
                    category_chart_data,
                    x='Net Expense',
                    y='Category',
                    title='Top 10 Categories by Net Expense',
                    orientation='h',
                    color='Net Expense',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # MONTHLY TREND ANALYSIS
        st.markdown('<div class="section-header">📈 Monthly Expense Trends</div>', unsafe_allow_html=True)
        
        monthly_summary = filtered_analysis.get_monthly_summary()
        
        if monthly_summary:
            monthly_df = pd.DataFrame(monthly_summary)
            
            # Line chart for monthly trends
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_df['month_name'],
                y=monthly_df['total_debit'],
                mode='lines+markers',
                name='Total Debit',
                line=dict(color='red', width=2),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_df['month_name'],
                y=monthly_df['total_credit'],
                mode='lines+markers',
                name='Total Credit',
                line=dict(color='green', width=2),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_df['month_name'],
                y=monthly_df['net_expense'],
                mode='lines+markers',
                name='Net Expense',
                line=dict(color='blue', width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title='Monthly Expense Trend',
                xaxis_title='Month',
                yaxis_title='Amount (₹)',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly summary table
            st.subheader("Monthly Breakdown")
            display_monthly_df = monthly_df.copy()
            display_monthly_df['total_debit'] = display_monthly_df['total_debit'].apply(lambda x: f"₹{x:,.2f}")
            display_monthly_df['total_credit'] = display_monthly_df['total_credit'].apply(lambda x: f"₹{x:,.2f}")
            display_monthly_df['net_expense'] = display_monthly_df['net_expense'].apply(lambda x: f"₹{x:,.2f}")
            
            display_monthly_df = display_monthly_df[['month_name', 'count', 'total_debit', 'total_credit', 'net_expense']]
            display_monthly_df.columns = ['Month', 'Transactions', 'Total Debit', 'Total Credit', 'Net Expense']
            
            st.dataframe(display_monthly_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # TOP EXPENSE PARTICULARS
        st.markdown('<div class="section-header">💰 Top Expense Items</div>', unsafe_allow_html=True)
        
        # Option to exclude Round Off
        exclude_roundoff = st.checkbox("Exclude 'Round Off' entries", value=True)
        
        exclude_list = ['Round Off'] if exclude_roundoff else []
        top_expenses = filtered_analysis.get_top_expenses_by_particular(top_n=20, exclude_particulars=exclude_list)
        
        if top_expenses:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Top expenses table
                top_exp_df = pd.DataFrame([
                    {
                        'Particular': item['particular'],
                        'Count': item['count'],
                        'Total Debit': f"₹{item['total_debit']:,.2f}",
                        'Total Credit': f"₹{item['total_credit']:,.2f}",
                        'Net Expense': f"₹{item['net_expense']:,.2f}",
                    }
                    for item in top_expenses
                ])
                st.dataframe(top_exp_df, use_container_width=True, hide_index=True, height=500)
            
            with col2:
                # Bar chart for top expenses
                top_exp_chart = pd.DataFrame(top_expenses[:10])
                
                fig = px.bar(
                    top_exp_chart,
                    x='net_expense',
                    y='particular',
                    title='Top 10 Expense Items by Amount',
                    orientation='h',
                    color='net_expense',
                    color_continuous_scale='Reds',
                    labels={'net_expense': 'Net Expense (₹)', 'particular': 'Expense Item'}
                )
                fig.update_layout(showlegend=False, height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # TRANSACTION TYPE ANALYSIS
        st.markdown('<div class="section-header">📝 Expense by Transaction Type</div>', unsafe_allow_html=True)
        
        txn_type_summary = filtered_analysis.get_transaction_type_summary()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Transaction type table
            txn_type_df = pd.DataFrame([
                {
                    'Transaction Type': txn_type,
                    'Transactions': data['count'],
                    'Total Debit': f"₹{data['total_debit']:,.2f}",
                    'Total Credit': f"₹{data['total_credit']:,.2f}",
                    'Net Expense': f"₹{data['net_expense']:,.2f}",
                }
                for txn_type, data in txn_type_summary.items()
            ])
            st.dataframe(txn_type_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Pie chart for transaction types
            txn_chart_data = pd.DataFrame([
                {'Type': txn_type, 'Net Expense': data['net_expense']}
                for txn_type, data in txn_type_summary.items()
            ])
            
            if not txn_chart_data.empty:
                fig = px.pie(
                    txn_chart_data,
                    values='Net Expense',
                    names='Type',
                    title='Net Expense by Transaction Type',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
