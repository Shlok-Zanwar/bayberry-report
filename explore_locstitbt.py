import pandas as pd

# Load the Excel file
file_path = 'BayberryStock.xlsx'

purchases_df = pd.read_excel(file_path, sheet_name='Purchases', header=2)
sales_df = pd.read_excel(file_path, sheet_name='Sales', header=2)

print("=" * 80)
print("DETAILED LOCSTITBT ANALYSIS")
print("=" * 80)

print(f"\nTotal Purchases rows: {len(purchases_df)}")
print(f"Non-null LOCSTITBT: {purchases_df['LOCSTITBT'].notna().sum()}")
print(f"Null LOCSTITBT: {purchases_df['LOCSTITBT'].isna().sum()}")

print("\nSample LOCSTITBT values (first 30 non-null):")
non_null_locstitbt = purchases_df[purchases_df['LOCSTITBT'].notna()]['LOCSTITBT'].head(30)
print(non_null_locstitbt.tolist())

print("\n\nSample comparison of BATCH NO vs LOCSTITBT (FG items):")
fg_items = purchases_df[purchases_df['ITEMTPCD'] == 'FG'][['ITEMCD', 'ITEMNAME', 'BATCH NO', 'LOCSTITBT', 'IN_QTY', 'IN_RATE']].head(20)
print(fg_items.to_string())

print("\n\n" + "=" * 80)
print("CHECKING ALL POSSIBLE BATCH FIELDS")
print("=" * 80)

# Check all columns with batch-related names
batch_related_cols = [col for col in purchases_df.columns if 'batch' in col.lower() or 'bt' in col.lower()]
print(f"\nBatch-related columns in Purchases: {batch_related_cols}")

for col in batch_related_cols:
    print(f"\n{col}:")
    print(f"  Non-null values: {purchases_df[col].notna().sum()}")
    print(f"  Sample values: {purchases_df[col].dropna().head(10).tolist()}")

print("\n\n" + "=" * 80)
print("TRYING TO UNDERSTAND THE LINKING MECHANISM")
print("=" * 80)

# Let's check if we need to link by Item Code AND some other field
print("\nApproach 1: Link by Item Code + Date range")
print("If a sale of item FG00002 happens on date X,")
print("we find the purchase of FG00002 that happened before date X")

# Sample
sample_item = 'FG00002'
print(f"\n\nExample with Item Code: {sample_item}")

purchase_sample = purchases_df[purchases_df['ITEMCD'] == sample_item][['ITEMCD', 'ITEMNAME', 'BATCH NO', 'LOCSTITBT', 'IN_QTY', 'IN_RATE', 'TXDATE']]
print(f"\nPurchases for {sample_item}:")
print(purchase_sample.to_string())

sales_sample = sales_df[sales_df['Item Code'] == sample_item][['Item Code', 'Item Name', 'Batch No.', 'Sale Qty.', 'Free Qty.', 'OUT_RATE', 'TXDATE']].head(10)
print(f"\n\nSales for {sample_item}:")
print(sales_sample.to_string())

print("\n\n" + "=" * 80)
print("CHECKING BTREFNO FIELD")
print("=" * 80)

print("\nBTREFNO might be the reference batch number")
print(f"Non-null BTREFNO: {purchases_df['BTREFNO'].notna().sum()}")
print(f"\nSample BTREFNO values:")
print(purchases_df[['ITEMCD', 'BATCH NO', 'BTREFNO', 'LOCSTITBT']].head(30).to_string())

# Check if BTREFNO matches sales batch
if purchases_df['BTREFNO'].notna().sum() > 0:
    purchase_btrefno = set(purchases_df['BTREFNO'].dropna().astype(str))
    sales_batches = set(sales_df['Batch No.'].dropna().astype(str))
    
    btrefno_matches = purchase_btrefno.intersection(sales_batches)
    print(f"\n\nMatches between BTREFNO and Sales Batch No.: {len(btrefno_matches)}")
    
    if len(btrefno_matches) > 0:
        print(f"Sample matches: {list(btrefno_matches)[:10]}")
