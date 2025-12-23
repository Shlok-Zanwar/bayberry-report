"""Vendor Rate Analysis - Product-wise Purchase Report."""
import streamlit as st
import pandas as pd
from pathlib import Path

from src.utils.auth import require_password
from src.services.excel_reader import ExcelReaderService
from src.services.data_transformer import DataTransformerService
from src.services.analysis import AnalysisService


# Page configuration
st.set_page_config(
    page_title="Vendor Analysis",
    page_icon="🔍",
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
    .product-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
    }
    .high-rate {
        background-color: #ffcccc !important;
    }
    .low-rate {
        background-color: #ccffcc !important;
    }
    .mid-rate {
        background-color: #ffffcc !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and transform data from Excel."""
    excel_file = Path('BayberryStock.xlsx')
    
    if not excel_file.exists():
        st.error(f"❌ Excel file not found: {excel_file}")
        st.stop()
    
    reader = ExcelReaderService(str(excel_file))
    purchases_df, sales_df = reader.load_data()
    
    transformer = DataTransformerService()
    purchases = transformer.transform_purchases(purchases_df)
    sales = transformer.transform_sales(sales_df)
    
    return purchases, sales


@st.cache_data
def get_vendor_analysis(_purchases, _sales, categories):
    """Get vendor and product analysis.
    
    Args:
        _purchases: List of purchases
        _sales: List of sales
        categories: Categories to analyze
    """
    analyzer = AnalysisService(_purchases, _sales)
    product_analysis = analyzer.get_product_wise_purchase_analysis(categories)
    vendor_analysis = analyzer.get_vendor_rate_analysis(categories)
    return product_analysis, vendor_analysis


def color_rate(row, min_rate, max_rate):
    """Apply color coding to rates based on position in range."""
    rate = row['purchase_rate']
    
    if max_rate == min_rate:
        return [''] * len(row)
    
    # Calculate position in range (0 to 1)
    position = (rate - min_rate) / (max_rate - min_rate)
    
    # Color cells based on rate
    styles = [''] * len(row)
    
    # Color the purchase_rate column
    rate_col_idx = list(row.index).index('purchase_rate')
    diff_col_idx = list(row.index).index('diff_from_min')
    
    if position > 0.66:  # Top 33% - Red (expensive)
        styles[rate_col_idx] = 'background-color: #ffcccc; font-weight: bold'
        styles[diff_col_idx] = 'background-color: #ffcccc; font-weight: bold'
    elif position < 0.33:  # Bottom 33% - Green (cheap)
        styles[rate_col_idx] = 'background-color: #ccffcc; font-weight: bold'
        styles[diff_col_idx] = 'background-color: #ccffcc; font-weight: bold'
    else:  # Middle - Yellow
        styles[rate_col_idx] = 'background-color: #ffffcc'
        styles[diff_col_idx] = 'background-color: #ffffcc'
    
    return styles


def main():
    """Main vendor analysis page."""
    
    # Header
    st.markdown('<div class="main-header">🔍 Vendor Rate Analysis</div>', unsafe_allow_html=True)
    st.markdown("Identify vendors charging higher rates for the same products")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        purchases, sales = load_data()
    
    # Detect anomalous rates FIRST (on raw data, before any filters)
    st.header("⚠️ Anomalous Purchase Rates - Data Quality Check")
    st.markdown("*Purchase records with rates < 50% of median rate for the same product (possible data errors or internal transfers)*")
    
    with st.spinner("Detecting anomalous rates..."):
        analyzer_raw = AnalysisService(purchases, sales)
        anomalies = analyzer_raw.detect_anomalous_purchase_rates(
            categories=['FG', 'TR'],
            threshold_pct=50.0,
            iterations=2
        )
    
    if anomalies:
        st.error(f"🚨 Found {len(anomalies)} suspicious purchase records that need review!")
        
        # Create DataFrame
        anomalies_df = pd.DataFrame(anomalies)
        
        # Format for display
        display_df = anomalies_df[[
            'batch_ref_no', 'item_name', 'vendor_name', 'purchase_rate', 
            'median_rate', 'rate_pct_of_median', 'purchase_qty', 
            'purchase_date', 'category', 'total_batches'
        ]].copy()
        
        display_df.columns = [
            'Batch No.', 'Product', 'Vendor', 'Purchase Rate', 
            'Median Rate', '% of Median', 'Qty', 
            'Date', 'Category', 'Total Batches'
        ]
        
        # Format numbers
        display_df['Purchase Rate'] = display_df['Purchase Rate'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Median Rate'] = display_df['Median Rate'].apply(lambda x: f"₹{x:,.2f}")
        display_df['% of Median'] = display_df['% of Median'].apply(lambda x: f"{x:.1f}%")
        
        # Color code by severity
        # def color_anomaly_row(row):
        #     pct = float(row['% of Median'].rstrip('%'))
        #     if pct < 20:
        #         return ['background-color: #ffcccc; font-weight: bold'] * len(row)
        #     elif pct < 35:
        #         return ['background-color: #ffe6cc'] * len(row)
        #     else:
        #         return ['background-color: #fff4cc'] * len(row)
        
        # styled_df = display_df.style.apply(color_anomaly_row, axis=1)
        styled_df = display_df
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=min(400, len(anomalies) * 35 + 38)
        )
        
        # Download button for anomalies
        csv = anomalies_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Anomalous Records (CSV)",
            data=csv,
            file_name="anomalous_purchase_rates.csv",
            mime="text/csv"
        )
        
        st.info("💡 **Action Required**: Review these records with your data entry team to fix errors or exclude these vendors if they are internal/related companies.")
    else:
        st.success("✅ No anomalous purchase rates detected!")
    
    st.markdown("---")
    
    # Sidebar filters for product/vendor selection
    st.sidebar.title("🎯 Display Filters")
    st.sidebar.markdown("---")
    
    # Category filter
    st.sidebar.subheader("Categories")
    include_fg = st.sidebar.checkbox("FG (Finished Goods)", value=True)
    include_tr = st.sidebar.checkbox("TR (Trading Goods)", value=True)
    
    categories = []
    if include_fg:
        categories.append('FG')
    if include_tr:
        categories.append('TR')
    
    if not categories:
        st.warning("⚠️ Please select at least one category")
        st.stop()
    
    # Get analysis
    with st.spinner("Analyzing vendor rates..."):
        product_analysis, vendor_analysis = get_vendor_analysis(purchases, sales, categories)
    
    products = product_analysis['products']
    vendors = vendor_analysis['vendors']
    
    # Summary Section
    st.header("📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Products Analyzed",
            f"{product_analysis['total_products']:,}",
            help="Number of unique products in selected categories"
        )
    
    with col2:
        multi_vendor_count = sum(1 for p in products if p['unique_vendors'] > 1)
        st.metric(
            "Multi-Vendor Products",
            f"{multi_vendor_count:,}",
            help="Products purchased from multiple vendors"
        )
    
    with col3:
        total_savings = sum(p['potential_savings'] for p in products)
        st.metric(
            "Potential Savings",
            f"₹{total_savings:,.0f}",
            help="If always bought at lowest rate",
            delta=f"{sum(p['potential_savings_pct'] for p in products) / len(products):.1f}%" if products else "0%"
        )
    
    with col4:
        avg_variance = sum(p['rate_variance_pct'] for p in products) / len(products) if products else 0
        st.metric(
            "Avg Rate Variance",
            f"{avg_variance:.1f}%",
            help="Average price difference across vendors"
        )
    
    st.markdown("---")
    
    # Vendor Performance Analysis
    st.header("🏆 Vendor Performance Analysis")
    st.markdown("*Analysis based on products purchased from multiple vendors*")
    
    if vendors:
        # Create vendor comparison table
        vendor_df = pd.DataFrame([{
            'Vendor': v['vendor_name'],
            'Products': v['total_products'],
            'Above Avg Rate': v['above_avg_count'],
            'Below Avg Rate': v['below_avg_count'],
            '% Above Avg': f"{v['above_avg_pct']:.1f}%",
            'Avg Diff from Product Avg': f"{v['avg_rate_diff_pct']:+.2f}%",
        } for v in vendors[:10]])  # Top 10 vendors
        
        st.dataframe(
            vendor_df,
            use_container_width=True,
            hide_index=True,
        )
        
        # Insights
        if vendors:
            most_expensive = vendors[0]
            most_cheap = vendors[-1]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.error(f"""
                **⚠️ Most Expensive Vendor**
                
                **{most_expensive['vendor_name']}**
                - Charges **{most_expensive['avg_rate_diff_pct']:+.2f}%** vs product average
                - Above average in **{most_expensive['above_avg_count']}/{most_expensive['total_products']}** products
                """)
            
            with col2:
                st.success(f"""
                **✅ Most Cost-Effective Vendor**
                
                **{most_cheap['vendor_name']}**
                - Charges **{most_cheap['avg_rate_diff_pct']:+.2f}%** vs product average
                - Below average in **{most_cheap['below_avg_count']}/{most_cheap['total_products']}** products
                """)
    else:
        st.info("ℹ️ No multi-vendor products found for comparison")
    
    st.markdown("---")
    
    # Top Products with High Rate Variance
    st.header("💰 Products with Highest Rate Variance")
    
    high_variance = [p for p in products if p['unique_vendors'] > 1][:10]
    
    if high_variance:
        variance_df = pd.DataFrame([{
            'Product': p['item_name'],
            'Vendors': p['unique_vendors'],
            'Min Rate': f"₹{p['min_rate']:.2f}",
            'Max Rate': f"₹{p['max_rate']:.2f}",
            'Variance': f"{p['rate_variance_pct']:.1f}%",
            'Potential Savings': f"₹{p['potential_savings']:,.0f}",
        } for p in high_variance])
        
        st.dataframe(
            variance_df,
            use_container_width=True,
            hide_index=True,
        )
    
    st.markdown("---")
    
    # Product-wise Purchase Details
    st.header("📦 Product-wise Purchase Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Product filter
        product_names = sorted(set(p['item_name'] for p in products))
        selected_products = st.multiselect(
            "Filter by Product",
            options=product_names,
            default=None,
            placeholder="All products"
        )
    
    with col2:
        # Vendor filter
        all_vendors = set()
        for p in products:
            all_vendors.update(p['vendor_avg_rates'].keys())
        vendor_names = sorted(all_vendors)
        
        selected_vendors = st.multiselect(
            "Filter by Vendor",
            options=vendor_names,
            default=None,
            placeholder="All vendors"
        )
    
    with col3:
        # Sort option
        sort_option = st.selectbox(
            "Sort products by",
            options=[
                "Rate Variance (High to Low)",
                "Rate Variance (Low to High)",
                "Product Name (A-Z)",
                "Potential Savings (High to Low)",
            ]
        )
    
    # Apply filters
    filtered_products = products
    
    if selected_products:
        filtered_products = [p for p in filtered_products if p['item_name'] in selected_products]
    
    if selected_vendors:
        filtered_products = [
            p for p in filtered_products
            if any(v in p['vendor_avg_rates'] for v in selected_vendors)
        ]
    
    # Apply sorting
    if sort_option == "Rate Variance (High to Low)":
        filtered_products = sorted(filtered_products, key=lambda x: x['rate_variance_pct'], reverse=True)
    elif sort_option == "Rate Variance (Low to High)":
        filtered_products = sorted(filtered_products, key=lambda x: x['rate_variance_pct'])
    elif sort_option == "Product Name (A-Z)":
        filtered_products = sorted(filtered_products, key=lambda x: x['item_name'])
    elif sort_option == "Potential Savings (High to Low)":
        filtered_products = sorted(filtered_products, key=lambda x: x['potential_savings'], reverse=True)
    
    st.info(f"📊 Showing {len(filtered_products)} of {len(products)} products")
    
    # Display each product
    for product in filtered_products:
        # Product header
        st.markdown(
            f"""<div class="product-header">
            {product['item_name']} 
            <span style="font-size: 0.9rem; color: #7f8c8d;">
            ({product['item_code']}) • {product['unique_vendors']} vendor(s) • 
            Rate: ₹{product['min_rate']:.2f} - ₹{product['max_rate']:.2f} 
            ({product['rate_variance_pct']:.1f}% variance)
            </span>
            </div>""",
            unsafe_allow_html=True
        )
        
        # Filter purchases by selected vendors
        display_purchases = product['purchases']
        if selected_vendors:
            display_purchases = [p for p in display_purchases if p.vendor_name in selected_vendors]
        
        if not display_purchases:
            st.write("*No purchases match the selected vendors*")
            continue
        
        # Create purchase details table
        purchase_data = []
        for p in display_purchases:
            purchase_data.append({
                'batch_ref_no': p.batch_ref_no,
                'vendor_name': p.vendor_name,
                'purchase_date': p.transaction_date.strftime('%Y-%m-%d') if p.transaction_date else '',
                'quantity': p.in_qty,
                'purchase_rate': p.in_rate,
                'total_cost': p.total_cost,
                'diff_from_min': ((p.in_rate - product['min_rate']) / product['min_rate'] * 100) if product['min_rate'] > 0 else 0,
            })
        
        purchase_df = pd.DataFrame(purchase_data)
        
        # Format dataframe
        formatted_df = purchase_df.copy()
        formatted_df['purchase_rate'] = formatted_df['purchase_rate'].apply(lambda x: f"₹{x:.2f}")
        formatted_df['total_cost'] = formatted_df['total_cost'].apply(lambda x: f"₹{x:,.0f}")
        formatted_df['diff_from_min'] = formatted_df['diff_from_min'].apply(lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%")
        
        # Rename columns for display
        formatted_df = formatted_df.rename(columns={
            'batch_ref_no': 'Batch No.',
            'vendor_name': 'Vendor',
            'purchase_date': 'Date',
            'quantity': 'Qty',
            'purchase_rate': 'Rate',
            'total_cost': 'Total Cost',
            'diff_from_min': 'Diff from Min',
        })
        
        # Apply color coding using original numeric data
        styled_df = purchase_df.style.apply(
            lambda row: color_rate(row, product['min_rate'], product['max_rate']),
            axis=1
        )
        
        # Format the styled dataframe
        styled_df = styled_df.format({
            'purchase_rate': '₹{:.2f}',
            'total_cost': '₹{:,.0f}',
            'diff_from_min': lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%",
        })
        
        # Rename columns
        styled_df = styled_df.set_table_attributes('class="dataframe"')
        
        # Display as HTML to preserve styling
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(
                formatted_df,
                use_container_width=True,
                hide_index=True,
            )
        
        with col2:
            st.markdown("**Summary**")
            st.markdown(f"**Purchases:** {len(display_purchases)}")
            st.markdown(f"**Total Qty:** {product['total_qty_purchased']:,}")
            st.markdown(f"**Avg Rate:** ₹{product['avg_rate']:.2f}")
            st.markdown(f"**Savings:** ₹{product['potential_savings']:,.0f}")
            if product['potential_savings_pct'] > 0:
                st.markdown(f"<span style='color: red;'>**({product['potential_savings_pct']:.1f}% saved)**</span>", unsafe_allow_html=True)
        
        st.markdown("")  # Spacing


if __name__ == "__main__":
    main()
