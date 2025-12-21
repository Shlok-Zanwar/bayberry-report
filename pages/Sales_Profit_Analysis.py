"""Sales Profit Analysis - Batch-wise Profit Dashboard."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from src.services.excel_reader import ExcelReaderService
from src.services.data_transformer import DataTransformerService
from src.services.profit_calculator import ProfitCalculatorService
from src.services.analysis import AnalysisService

# Page configuration
st.set_page_config(
    page_title="Sales Profit Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add navigation hint
st.sidebar.success("👈 Use the sidebar to navigate")

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
    /* Fix metric card styling */
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process data with caching."""
    excel_path = Path("BayberryStock.xlsx")
    # Read Excel
    reader = ExcelReaderService(str(excel_path))
    purchases_df, sales_df = reader.load_data()
    # Transform to domain models
    transformer = DataTransformerService()
    purchases = transformer.transform_purchases(purchases_df)
    sales = transformer.transform_sales(sales_df)
    return purchases, sales, reader.get_summary()

@st.cache_data
def calculate_profits(_purchases, _sales, categories):
    """Calculate batch profits with caching."""
    calculator = ProfitCalculatorService(_purchases, _sales)
    batch_profits = calculator.calculate_batch_profits(include_categories=categories)
    summary_by_category = calculator.get_summary_by_category(batch_profits)
    overall_summary = calculator.get_summary_stats(batch_profits)
    return batch_profits, summary_by_category, overall_summary

@st.cache_data
def get_analysis_data(_purchases, _sales):
    """Get additional analysis data with caching."""
    analyzer = AnalysisService(_purchases, _sales)
    fg_tr_orphans, other_orphans = analyzer.get_orphan_sales()
    charges_report = analyzer.create_charges_report()
    return analyzer, fg_tr_orphans, other_orphans, charges_report

def format_batch_profits_dataframe(profits_df):
    """Format batch profits dataframe with proper column order and formatting.
    To change column order, simply rearrange items in the COLUMN_ORDER list.
    """
    # Define column order - change the order here to reorder columns in display
    COLUMN_ORDER = [
        'batch_ref_no',
        'item_name',
        'purchase_qty',
        'purchase_rate',
        'purchase_cost',
        'total_sale_qty',
        'total_free_qty',
        'total_out_qty',
        'remaining_qty',
        'avg_sale_rate',
        'revenue_from_sales',
        'total_cogs',
        'total_cost_due_to_free',
        'total_cost_due_to_discount',
        'profit',
        'profit_margin',
        'gross_revenue',
        'net_revenue',
        'status',
        'category',
        'item_code',
        'vendor_name',
        'purchase_date',
    ]
    # Column display names
    COLUMN_NAMES = {
        'batch_ref_no': 'Batch No.',
        'item_code': 'Item Code',
        'item_name': 'Item Name',
        'category': 'Category',
        'vendor_name': 'Vendor',
        'purchase_date': 'Purchase Date',
        'purchase_qty': 'Purchase Qty',
        'purchase_rate': 'Purchase Rate',
        'purchase_cost': 'Total Purchase Cost',
        'total_sale_qty': 'Sale Qty',
        'total_free_qty': 'Free Qty',
        'total_out_qty': 'Total Out Qty',
        'remaining_qty': 'Remaining Qty',
        'avg_sale_rate': 'Avg Sale Rate',
        'revenue_from_sales': 'Revenue from Sales',
        'total_cogs': 'COGS',
        'total_cost_due_to_free': 'Cost (Free) - Ref',
        'total_cost_due_to_discount': 'Cost (Discount)',
        'profit': 'Profit',
        'profit_margin': 'Margin %',
        'gross_revenue': 'Gross Revenue (w/ GST)',
        'net_revenue': 'Net Revenue (Legacy)',
        'status': 'Status'
    }
    # Reorder columns
    df = profits_df[COLUMN_ORDER].copy()
    # Format currency columns with 2 decimal places for rates
    rate_cols = ['purchase_rate', 'avg_sale_rate']
    for col in rate_cols:
        df[col] = df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "")
    # Format other currency columns with no decimal places
    currency_cols = ['purchase_cost', 'gross_revenue', 'net_revenue', 'revenue_from_sales',
                     'total_cogs', 'total_cost_due_to_free', 'total_cost_due_to_discount', 'profit']
    for col in currency_cols:
        df[col] = df[col].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "")
    # Format percentage
    df['profit_margin'] = df['profit_margin'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    # Format quantities
    qty_cols = ['purchase_qty', 'total_sale_qty', 'total_free_qty', 'total_out_qty', 'remaining_qty']
    for col in qty_cols:
        df[col] = df[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
    # Rename columns
    df = df.rename(columns=COLUMN_NAMES)
    return df

def main():
    """Main dashboard function."""
    # Header
    st.markdown('<div class="main-header">💰 Sales Profit Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Batch-wise Profit Analysis** • View vendor rate analysis in the sidebar →")
    st.markdown("---")
    # Load data
    with st.spinner("Loading data..."):
        purchases, sales, data_summary = load_data()
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    st.sidebar.markdown("---")
    # Category filter
    st.sidebar.subheader("Categories to Analyze")
    include_fg = st.sidebar.checkbox("FG (Finished Goods)", value=True)
    include_tr = st.sidebar.checkbox("TR (Trading Goods)", value=True)
    categories = []
    if include_fg:
        categories.append('FG')
    if include_tr:
        categories.append('TR')
    if not categories:
        st.error("⚠️ Please select at least one category to analyze!")
        return
    # Calculate profits
    with st.spinner("Calculating profits..."):
        batch_profits, summary_by_category, overall_summary = calculate_profits(
            purchases, sales, categories
        )
    # Get analysis data
    with st.spinner("Preparing additional reports..."):
        analyzer, fg_tr_orphans, other_orphans, charges_report = get_analysis_data(
            purchases, sales
        )
    # Convert to DataFrame for display
    profits_df = pd.DataFrame([bp.to_dict() for bp in batch_profits])
    # Summary Section
    st.header("📈 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Batches",
            f"{overall_summary['total_batches']:,}",
            help="Total number of batches analyzed"
        )
    with col2:
        st.metric(
            "Total Purchase Cost",
            f"₹{overall_summary['total_purchase_cost']:,.0f}",
            help="Total cost of all purchases"
        )
    with col3:
        st.metric(
            "Total Revenue",
            f"₹{overall_summary['total_revenue']:,.0f}",
            help="Total net revenue from sales"
        )
    with col4:
        profit_color = "normal" if overall_summary['total_profit'] >= 0 else "inverse"
        st.metric(
            "Total Profit",
            f"₹{overall_summary['total_profit']:,.0f}",
            f"{overall_summary['avg_profit_margin']:.1f}%",
            delta_color=profit_color,
            help="Total profit and average profit margin"
        )
    # Profit Distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Profit Distribution")
        profit_dist_data = {
            'Status': ['Profit', 'Loss', 'Breakeven'],
            'Count': [
                overall_summary['batches_with_profit'],
                overall_summary['batches_with_loss'],
                overall_summary['batches_breakeven']
            ]
        }
        fig_dist = px.pie(
            profit_dist_data,
            values='Count',
            names='Status',
            color='Status',
            color_discrete_map={'Profit': 'green', 'Loss': 'red', 'Breakeven': 'gray'}
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    with col2:
        st.subheader("Category-wise Performance")
        if summary_by_category:
            cat_data = []
            for cat, data in summary_by_category.items():
                cat_data.append({
                    'Category': cat,
                    'Profit': data['total_profit'],
                    'Revenue': data['total_revenue'],
                    'Margin %': data['avg_profit_margin']
                })
            cat_df = pd.DataFrame(cat_data)
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(
                x=cat_df['Category'],
                y=cat_df['Profit'],
                name='Profit',
                marker_color='green'
            ))
            fig_cat.update_layout(
                xaxis_title="Category",
                yaxis_title="Profit (₹)",
                showlegend=False
            )
            st.plotly_chart(fig_cat, use_container_width=True)
    st.markdown("---")
    # Batch-wise Profit Table
    st.header("🔍 Batch-wise Profit Analysis")
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=profits_df['status'].unique().tolist(),
            default=profits_df['status'].unique().tolist()
        )
    with col2:
        category_filter = st.multiselect(
            "Filter by Category",
            options=profits_df['category'].unique().tolist(),
            default=profits_df['category'].unique().tolist()
        )
    with col3:
        min_profit = float(profits_df['profit'].min())
        max_profit = float(profits_df['profit'].max())
        profit_range = st.slider(
            "Profit Range (₹)",
            min_value=min_profit,
            max_value=max_profit,
            value=(min_profit, max_profit)
        )
    # Apply filters
    filtered_df = profits_df[
        (profits_df['status'].isin(status_filter)) &
        (profits_df['category'].isin(category_filter)) &
        (profits_df['profit'] >= profit_range[0]) &
        (profits_df['profit'] <= profit_range[1])
    ]
    st.info(f"📊 Showing {len(filtered_df)} of {len(profits_df)} batches")
    # Format the dataframe for display
    display_df = format_batch_profits_dataframe(filtered_df)
    # Store the mapping of display index to batch_ref_no before displaying
    batch_mapping = filtered_df['batch_ref_no'].reset_index(drop=True).to_dict()
    # Display the table with row selection enabled
    st.write("**Click on a row to view detailed analysis**")
    selected_rows = st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=False,
        on_select="rerun",
        selection_mode="single-row"
    )
    # Show selected row details
    selected_idx = None
    if selected_rows and 'selection' in selected_rows and 'rows' in selected_rows['selection']:
        if len(selected_rows['selection']['rows']) > 0:
            selected_idx = selected_rows['selection']['rows'][0]
    if selected_idx is not None:
        st.markdown("---")
        st.header("📋 Detailed Batch Analysis")
        # Get the batch number from the mapping
        batch_no = batch_mapping[selected_idx]
        # Find the batch profit object
        batch_profit = next((bp for bp in batch_profits if bp.batch_ref_no == batch_no), None)
        if batch_profit:
            # Summary Section
            st.subheader(f"🔍 Batch: {batch_no}")
            st.write(f"**Item:** {batch_profit.item_name} ({batch_profit.item_code})")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Purchase Qty", f"{batch_profit.purchase_qty:,}")
            with col2:
                st.metric("Sold Qty", f"{batch_profit.total_sale_qty:,}")
            with col3:
                st.metric("Free Qty", f"{batch_profit.total_free_qty:,}")
            with col4:
                st.metric("Remaining", f"{batch_profit.remaining_qty:,}")
            # Sales Details Table
            st.markdown("---")
            st.subheader("📊 Individual Sales Breakdown")
            if batch_profit.sale_details:
                sales_detail_data = [sd.to_dict() for sd in batch_profit.sale_details]
                sales_detail_df = pd.DataFrame(sales_detail_data)
                # Format sales detail dataframe for display
                sales_display = sales_detail_df.copy()
                # Format currency columns
                currency_cols = ['out_rate', 'gross_value', 'discount_value', 'revenue_from_sale',
                                'cost_of_goods_sold', 'cost_due_to_free', 'cost_due_to_discount', 'final_profit']
                for col in currency_cols:
                    if col in sales_display.columns:
                        sales_display[col] = sales_display[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "")
                # Format quantity columns
                qty_cols = ['sale_qty', 'free_qty', 'out_qty']
                for col in qty_cols:
                    if col in sales_display.columns:
                        sales_display[col] = sales_display[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
                # Rename columns for better display
                column_renames = {
                    'sale_qty': 'Sale Qty',
                    'free_qty': 'Free Qty',
                    'out_qty': 'Out Qty',
                    'out_rate': 'Sale Rate',
                    'gross_value': 'Gross Value (w/ GST)',
                    'discount_value': 'Discount',
                    'revenue_from_sale': 'Revenue from Sale',
                    'cost_of_goods_sold': 'COGS',
                    'cost_due_to_free': 'Cost (Free)',
                    'cost_due_to_discount': 'Cost (Discount)',
                    'final_profit': 'Final Profit'
                }
                sales_display = sales_display.rename(columns=column_renames)
                st.dataframe(
                    sales_display,
                    use_container_width=True,
                    height=400
                )
                # Download sales details
                csv_sales = sales_detail_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Sales Details",
                    data=csv_sales,
                    file_name=f"sales_details_{batch_no}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No sales records found for this batch")
            # Profit Breakdown Summary
            st.markdown("---")
            st.subheader("💰 Profit Breakdown Summary")
            col1, col2 = st.columns([2, 1])
            with col1:
                # Waterfall chart
                breakdown_data = {
                    'Component': [
                        'Revenue from Sales',
                        'COGS',
                        'Cost Due to Discount',
                        'Final Profit'
                    ],
                    'Amount': [
                        batch_profit.revenue_from_sales,
                        -batch_profit.total_cogs,
                        -batch_profit.total_cost_due_to_discount,
                        batch_profit.profit
                    ]
                }
                fig_breakdown = go.Figure(go.Waterfall(
                    orientation="v",
                    measure=["relative", "relative", "relative", "total"],
                    x=breakdown_data['Component'],
                    y=breakdown_data['Amount'],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                    increasing={"marker": {"color": "green"}},
                    decreasing={"marker": {"color": "red"}},
                    totals={"marker": {"color": "blue"}},
                ))
                fig_breakdown.update_layout(
                    title="Profit Waterfall",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_breakdown, use_container_width=True)
            with col2:
                st.markdown("##### Profit Calculation")
                st.metric("Revenue from Sales", f"₹{batch_profit.revenue_from_sales:,.0f}")
                st.metric("COGS (All Out Qty)", f"₹{batch_profit.total_cogs:,.0f}", delta_color="inverse")
                st.metric("Cost (Free) - Ref", f"₹{batch_profit.total_cost_due_to_free:,.0f}", help="Included in COGS for visibility")
                st.metric("Cost (Discount)", f"₹{batch_profit.total_cost_due_to_discount:,.0f}", delta_color="inverse")
                st.markdown("---")
                profit_color = "normal" if batch_profit.profit >= 0 else "inverse"
                st.metric("**Final Profit**", f"₹{batch_profit.profit:,.0f}", f"{batch_profit.profit_margin:.1f}%", delta_color=profit_color)
            # Other Purchase Details
            st.markdown("---")
            st.subheader("📦 Other Items in Same Batch")
            fg_tr_purchases, other_purchases = analyzer.get_other_batch_purchases(batch_no)
            if other_purchases:
                st.markdown("##### Non-FG/TR Purchase Items (Charges)")
                other_purchase_data = []
                for p in other_purchases:
                    other_purchase_data.append({
                        'category': p.category,
                        'item_code': p.item_code,
                        'item_name': p.item_name,
                        'qty': p.in_qty,
                        'rate': round(p.in_rate, 2),
                        'value': round(p.gross_value, 2),
                    })
                other_purchase_df = pd.DataFrame(other_purchase_data)
                st.dataframe(other_purchase_df, use_container_width=True)
            else:
                st.info("No charge items (SV/CO/CG) found in this batch")
            if len(fg_tr_purchases) > 1:
                st.markdown("##### All FG/TR Purchases in This Batch")
                st.info(f"Found {len(fg_tr_purchases)} FG/TR items sharing this batch reference")
                fg_tr_data = []
                for p in fg_tr_purchases:
                    fg_tr_data.append({
                        'item_code': p.item_code,
                        'item_name': p.item_name,
                        'qty': p.in_qty,
                        'rate': round(p.in_rate, 2),
                        'value': round(p.gross_value, 2),
                    })
                fg_tr_df = pd.DataFrame(fg_tr_data)
                st.dataframe(fg_tr_df, use_container_width=True)
    # Export functionality
    st.markdown("---")
    st.subheader("📥 Export Data")
    col1, col2 = st.columns([1, 4])
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="batch_profits.csv",
            mime="text/csv"
        )
    # Orphan Sales Report
    st.markdown("---")
    st.header("⚠️ Sales Without Purchase Records (FG/TR)")
    if fg_tr_orphans:
        st.warning(f"Found {len(fg_tr_orphans)} FG/TR sales without matching purchase records")
        orphan_df = analyzer.create_orphan_sales_report(fg_tr_orphans)
        # Show summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Orphan Sales", len(fg_tr_orphans))
        with col2:
            total_orphan_value = orphan_df['gross_value'].sum()
            st.metric("Total Value", f"₹{total_orphan_value:,.0f}")
        with col3:
            unique_batches = orphan_df['batch_no'].nunique()
            st.metric("Unique Batches", unique_batches)
        # Show table
        st.dataframe(orphan_df, use_container_width=True, height=400)
        # Download
        csv_orphan = orphan_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Orphan Sales Report",
            data=csv_orphan,
            file_name="orphan_sales_fg_tr.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ All FG/TR sales have matching purchase records!")
    # Charges Analysis
    st.markdown("---")
    st.header("💼 Charges Analysis (SV/CO/CG)")
    if charges_report['purchases'] or charges_report['sales']:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Purchase Charges")
            if charges_report['purchases']:
                purchase_charge_data = []
                for cat, data in charges_report['purchases'].items():
                    purchase_charge_data.append({
                        'Category': cat,
                        'Count': data['count'],
                        'Total Qty': data['total_qty'],
                        'Total Value': round(data['total_value'], 2),
                    })
                purchase_charge_df = pd.DataFrame(purchase_charge_data)
                st.dataframe(purchase_charge_df, use_container_width=True)
                total_purchase_charges = sum(d['total_value'] for d in charges_report['purchases'].values())
                st.metric("Total Purchase Charges", f"₹{total_purchase_charges:,.0f}")
            else:
                st.info("No purchase charges found")
        with col2:
            st.subheader("Sales Charges")
            if charges_report['sales']:
                sales_charge_data = []
                for cat, data in charges_report['sales'].items():
                    sales_charge_data.append({
                        'Category': cat,
                        'Count': data['count'],
                        'Total Qty': data['total_qty'],
                        'Total Value': round(data['total_value'], 2),
                    })
                sales_charge_df = pd.DataFrame(sales_charge_data)
                st.dataframe(sales_charge_df, use_container_width=True)
                total_sales_charges = sum(d['total_value'] for d in charges_report['sales'].values())
                st.metric("Total Sales Charges", f"₹{total_sales_charges:,.0f}")
            else:
                st.info("No sales charges found")
        # Net charge analysis
        if charges_report['purchases'] and charges_report['sales']:
            st.markdown("---")
            st.subheader("Net Charge Analysis")
            total_purchase_charges = sum(d['total_value'] for d in charges_report['purchases'].values())
            total_sales_charges = sum(d['total_value'] for d in charges_report['sales'].values())
            net_charges = total_sales_charges - total_purchase_charges
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Charges Paid", f"₹{total_purchase_charges:,.0f}")
            with col2:
                st.metric("Total Charges Recovered", f"₹{total_sales_charges:,.0f}")
            with col3:
                delta_color = "normal" if net_charges >= 0 else "inverse"
                st.metric("Net Impact", f"₹{net_charges:,.0f}", delta_color=delta_color)
    else:
        st.info("No charge items found in the dataset")

if __name__ == "__main__":
    main()
