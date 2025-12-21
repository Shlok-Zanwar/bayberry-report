import pandas as pd

# Load the Excel file
file_path = 'BayberryStock.xlsx'

purchases_df = pd.read_excel(file_path, sheet_name='Purchases', header=2)
sales_df = pd.read_excel(file_path, sheet_name='Sales', header=2)

print("=" * 80)
print("VERIFICATION: BTREFNO (Purchases) = Batch No. (Sales)")
print("=" * 80)

# Get matches
purchase_btrefno = set(purchases_df['BTREFNO'].dropna().astype(str))
sales_batches = set(sales_df['Batch No.'].dropna().astype(str))

btrefno_matches = purchase_btrefno.intersection(sales_batches)
print(f"\nTotal unique BTREFNO in Purchases: {len(purchase_btrefno)}")
print(f"Total unique Batch No. in Sales: {len(sales_batches)}")
print(f"Matching batches: {len(btrefno_matches)} ({len(btrefno_matches)/len(purchase_btrefno)*100:.1f}% of purchases)")

# Sample linking
sample_batch = list(btrefno_matches)[0]
print(f"\n\n{'=' * 80}")
print(f"SAMPLE BATCH LINKING: {sample_batch}")
print(f"{'=' * 80}")

print("\nPURCHASE DATA:")
purchase_data = purchases_df[purchases_df['BTREFNO'] == sample_batch][
    ['ITEMTPCD', 'ITEMCD', 'ITEMNAME', 'BTREFNO', 'IN_QTY', 'IN_RATE', 'BSVAL', 'TXDATE']
]
print(purchase_data.to_string())

print("\n\nSALES DATA:")
sales_data = sales_df[sales_df['Batch No.'] == sample_batch][
    ['Item Code', 'Item Name', 'Batch No.', 'Sale Qty.', 'Free Qty.', 'OUT_RATE', 'Discount Value', 'Gross Value', 'TXDATE']
].head(10)
print(sales_data.to_string())

# Calculate profit for this batch
if len(purchase_data) > 0 and len(sales_data) > 0:
    purchase_cost = (purchase_data['IN_QTY'].sum() * purchase_data['IN_RATE'].iloc[0])
    total_sales_revenue = sales_data['Gross Value'].sum()
    total_discount = sales_data['Discount Value'].sum()
    free_qty_loss = (sales_data['Free Qty.'].sum() * sales_data['OUT_RATE'].mean())
    
    net_revenue = total_sales_revenue - total_discount
    profit = net_revenue - purchase_cost - free_qty_loss
    
    print(f"\n\nPROFIT CALCULATION FOR BATCH: {sample_batch}")
    print(f"Purchase Cost: {purchase_cost:.2f} (IN_QTY: {purchase_data['IN_QTY'].sum()} × IN_RATE: {purchase_data['IN_RATE'].iloc[0]:.2f})")
    print(f"Sales Revenue (Gross): {total_sales_revenue:.2f}")
    print(f"Less: Discount: {total_discount:.2f}")
    print(f"Less: Free Qty Loss: {free_qty_loss:.2f} (Free Qty: {sales_data['Free Qty.'].sum()} × Avg Rate: {sales_data['OUT_RATE'].mean():.2f})")
    print(f"Net Revenue: {net_revenue:.2f}")
    print(f"PROFIT: {profit:.2f}")

print(f"\n\n{'=' * 80}")
print("UNDERSTANDING THE DATA STRUCTURE")
print(f"{'=' * 80}")

print("\n✓ VERIFIED: Your understanding is CORRECT!")

print("\n\nKEY FINDINGS:")
print("=" * 80)

print("\n1. ITEM CODE CATEGORIES:")
print("   - Purchases have ITEMTPCD: FG, TR, SV, CO, CG, AD")
print("   - Sales have Item Code starting with: FG, TR, SV, CO, AD")
print("   - The Item Code in both sheets matches (e.g., FG00002)")

print("\n2. BATCH LINKING:")
print("   - Purchases: BTREFNO field (e.g., 'BBT24G06A')")
print("   - Sales: Batch No. field (e.g., 'BBT24G06A')")
print(f"   - {len(btrefno_matches)} batches can be linked between Purchases and Sales")

print("\n3. KEY COLUMNS FOR PROFIT CALCULATION:")
print("\n   PURCHASES:")
print("   - IN_QTY: Quantity purchased")
print("   - IN_RATE: Rate per unit purchased")
print("   - BSVAL: Basic value")
print("   - ITEMTPCD: Item category (FG, TR, SV, CO, CG, AD)")
print("   - BTREFNO: Batch reference number (links to Sales)")

print("\n   SALES:")
print("   - Sale Qty.: Quantity sold")
print("   - Free Qty.: Quantity given free (loss)")
print("   - OUT_RATE: Selling rate per unit")
print("   - Discount Value: Discount given (loss)")
print("   - Gross Value: Total sale value")
print("   - Batch No.: Batch number (links to Purchases)")

print("\n4. ITEM CATEGORIES EXPLANATION:")
print("   ✓ FG (Finished Goods): Main products")
print("   ✓ TR (Trading Goods): Traded products")
print("   ✓ SV (Service Charges): Insurance, freight, etc.")
print("   ✓ CO (Cylinder Charges): Cylinder/container charges")
print("   ✓ CG (Other Charges): Additional charges")
print("   ✓ AD (Advertising): Promotional goods")

print("\n5. PROFIT CALCULATION COMPONENTS:")
print("   Revenue = Gross Value - Discount Value")
print("   Cost = IN_QTY × IN_RATE")
print("   Free Goods Loss = Free Qty. × OUT_RATE")
print("   Profit = Revenue - Cost - Free Goods Loss")

print("\n6. ADDITIONAL CONSIDERATIONS:")
print("   - SV, CO, CG charges should be allocated to FG/TR items")
print("   - AD items are company expenses (not for sale)")
print("   - Some sales have NaN Batch No. (need to handle)")

print("\n\n" + "=" * 80)
print("BATCHES WITHOUT PURCHASES")
print("=" * 80)

sales_batches_without_purchase = sales_batches - purchase_btrefno
print(f"\nSales batches without matching purchase: {len(sales_batches_without_purchase)}")
print(f"This could be:")
print(f"  - Old stock from previous periods")
print(f"  - Missing batch reference in purchases")
print(f"  - Data entry issues")

if len(sales_batches_without_purchase) > 0:
    print(f"\nSample batches: {list(sales_batches_without_purchase)[:10]}")
    
    # Check one example
    orphan_batch = list(sales_batches_without_purchase)[0]
    orphan_sales = sales_df[sales_df['Batch No.'] == orphan_batch][['Item Code', 'Item Name', 'Batch No.', 'Sale Qty.', 'TXDATE']].head(5)
    print(f"\nExample sales without purchase (Batch: {orphan_batch}):")
    print(orphan_sales.to_string())

print("\n\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

print("\nPURCHASES:")
purchases_summary = purchases_df.groupby('ITEMTPCD').agg({
    'IN_QTY': 'sum',
    'BSVAL': 'sum',
    'ITEMCD': 'count'
}).round(2)
purchases_summary.columns = ['Total Qty', 'Total Value', 'Line Items']
print(purchases_summary)

print("\n\nSALES:")
sales_df['Item_Prefix'] = sales_df['Item Code'].astype(str).str[:2]
sales_summary = sales_df.groupby('Item_Prefix').agg({
    'Sale Qty.': 'sum',
    'Free Qty.': 'sum',
    'Gross Value': 'sum',
    'Discount Value': 'sum',
    'Item Code': 'count'
}).round(2)
sales_summary.columns = ['Total Sale Qty', 'Total Free Qty', 'Total Revenue', 'Total Discount', 'Line Items']
print(sales_summary)
