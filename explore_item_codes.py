import pandas as pd

# Load the Excel file
file_path = 'BayberryStock.xlsx'

print("=" * 80)
print("ITEM CODE ANALYSIS - PURCHASES")
print("=" * 80)

purchases_df = pd.read_excel(file_path, sheet_name='Purchases', header=2)

print("\nItem Code column analysis:")
print(f"Column name: 'ITEMCD'")
print(f"Total rows: {len(purchases_df)}")
print(f"Non-null ITEMCD: {purchases_df['ITEMCD'].notna().sum()}")

# Check ITEMTPCD column (Item Type Code)
print("\n\nITEMTPCD (Item Type Code) analysis:")
print(purchases_df['ITEMTPCD'].value_counts())

print("\n\nSample data showing ITEMTPCD vs ITEMCD:")
print(purchases_df[['ITEMTPCD', 'ITEMCD', 'ITEMNAME', 'BATCH NO', 'IN_QTY', 'IN_RATE']].head(20))

# Check relationship between ITEMTPCD and ITEMCD
print("\n\nChecking if ITEMCD starts with ITEMTPCD:")
for item_type in ['FG', 'TR', 'SV', 'CO', 'CG', 'AD']:
    subset = purchases_df[purchases_df['ITEMTPCD'] == item_type]
    if len(subset) > 0:
        print(f"\n{item_type}: {len(subset)} rows")
        sample_codes = subset['ITEMCD'].head(5).tolist()
        print(f"  Sample ITEMCD: {sample_codes}")

print("\n" + "=" * 80)
print("ITEM CODE ANALYSIS - SALES")
print("=" * 80)

sales_df = pd.read_excel(file_path, sheet_name='Sales', header=2)

print("\nItem Code column analysis:")
print(f"Column name: 'Item Code'")
print(f"Total rows: {len(sales_df)}")
print(f"Non-null Item Code: {sales_df['Item Code'].notna().sum()}")

print("\n\nSample data showing Item Code and related columns:")
print(sales_df[['Item Code', 'Item Name', 'Batch No.', 'Sale Qty.', 'Free Qty.', 'OUT_QTY', 'OUT_RATE', 'Discount Value']].head(20))

print("\n" + "=" * 80)
print("LINKING ANALYSIS - Can we link Sales to Purchases?")
print("=" * 80)

print("\n1. By Item Code:")
# Try to find matching pattern
sales_item_codes = set(sales_df['Item Code'].dropna().astype(str))
purchase_item_codes = set(purchases_df['ITEMCD'].dropna().astype(str))

# Check exact matches
exact_matches = sales_item_codes.intersection(purchase_item_codes)
print(f"   Exact Item Code matches: {len(exact_matches)}")

print("\n2. By Batch Number:")
sales_batches = set(sales_df['Batch No.'].dropna().astype(str))
purchase_batches = set(purchases_df['BATCH NO'].dropna().astype(str))

batch_matches = sales_batches.intersection(purchase_batches)
print(f"   Exact Batch matches: {len(batch_matches)}")
print(f"   Unique batches in Sales: {len(sales_batches)}")
print(f"   Unique batches in Purchases: {len(purchase_batches)}")

print("\n3. Sample batch linking:")
# Find a common batch and show data
if len(batch_matches) > 0:
    sample_batch = list(batch_matches)[0]
    print(f"\n   Sample Batch: {sample_batch}")
    
    print("\n   In Purchases:")
    purchase_sample = purchases_df[purchases_df['BATCH NO'] == sample_batch][['ITEMTPCD', 'ITEMCD', 'ITEMNAME', 'BATCH NO', 'IN_QTY', 'IN_RATE', 'TXDATE']]
    print(purchase_sample)
    
    print("\n   In Sales:")
    sales_sample = sales_df[sales_df['Batch No.'] == sample_batch][['Item Code', 'Item Name', 'Batch No.', 'Sale Qty.', 'Free Qty.', 'OUT_RATE', 'TXDATE']].head(10)
    print(sales_sample)

print("\n" + "=" * 80)
print("UNDERSTANDING THE CATEGORY CODES")
print("=" * 80)

print("\nPurchases - ITEMTPCD (Category) breakdown:")
itemtpcd_summary = purchases_df.groupby('ITEMTPCD').agg({
    'IN_QTY': 'sum',
    'IN_RATE': 'mean',
    'GRVAL': 'sum',
    'ITEMCD': 'count'
}).round(2)
itemtpcd_summary.columns = ['Total IN_QTY', 'Avg IN_RATE', 'Total GRVAL', 'Row Count']
print(itemtpcd_summary)

print("\n\nSales - Item Code prefix breakdown:")
sales_df['Item_Prefix'] = sales_df['Item Code'].astype(str).str[:2]
prefix_summary = sales_df.groupby('Item_Prefix').agg({
    'Sale Qty.': 'sum',
    'Free Qty.': 'sum',
    'OUT_RATE': 'mean',
    'Gross Value': 'sum',
    'Discount Value': 'sum',
    'Item Code': 'count'
}).round(2)
prefix_summary.columns = ['Total Sale Qty', 'Total Free Qty', 'Avg OUT_RATE', 'Total Gross Value', 'Total Discount', 'Row Count']
print(prefix_summary)
