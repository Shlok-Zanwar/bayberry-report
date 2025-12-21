import pandas as pd

# Load the Excel file
file_path = 'BayberryStock.xlsx'

purchases_df = pd.read_excel(file_path, sheet_name='Purchases', header=2)
sales_df = pd.read_excel(file_path, sheet_name='Sales', header=2)

print("=" * 80)
print("BATCH NUMBER FORMAT INVESTIGATION")
print("=" * 80)

# Let's look at the batch formats more carefully
print("\nPurchases - Sample Batches by Item Type:")
for item_type in ['FG', 'TR', 'SV', 'CO', 'CG', 'AD']:
    subset = purchases_df[purchases_df['ITEMTPCD'] == item_type]
    if len(subset) > 0:
        print(f"\n{item_type}:")
        sample = subset[['ITEMCD', 'ITEMNAME', 'BATCH NO', 'TXDATE']].head(3)
        print(sample.to_string())

print("\n\n" + "=" * 80)
print("Sales - Sample Batches by Item Code Prefix:")
print("=" * 80)
sales_df['Item_Prefix'] = sales_df['Item Code'].astype(str).str[:2]
for prefix in ['FG', 'TR', 'SV', 'CO', 'AD']:
    subset = sales_df[sales_df['Item_Prefix'] == prefix]
    if len(subset) > 0:
        print(f"\n{prefix}:")
        sample = subset[['Item Code', 'Item Name', 'Batch No.', 'TXDATE']].head(3)
        print(sample.to_string())

# Check if batches in sales follow a different format
print("\n\n" + "=" * 80)
print("CHECKING LOCSTITBT FIELD IN PURCHASES")
print("=" * 80)

# LOCSTITBT might be the actual batch number used in sales
print("\nLOCSTITBT sample data:")
print(purchases_df[['ITEMTPCD', 'ITEMCD', 'BATCH NO', 'LOCSTITBT', 'TXDATE']].head(20))

print("\nChecking if LOCSTITBT matches Sales Batch No.:")
if 'LOCSTITBT' in purchases_df.columns:
    purchase_locstitbt = set(purchases_df['LOCSTITBT'].dropna().astype(str))
    sales_batches = set(sales_df['Batch No.'].dropna().astype(str))
    
    locstitbt_matches = purchase_locstitbt.intersection(sales_batches)
    print(f"Matches between LOCSTITBT and Sales Batch No.: {len(locstitbt_matches)}")
    
    if len(locstitbt_matches) > 0:
        print(f"\nFound matches! Sample: {list(locstitbt_matches)[:5]}")
        
        # Show a linking example
        sample_batch = list(locstitbt_matches)[0]
        print(f"\n\nExample linking for batch: {sample_batch}")
        
        print("\nIn Purchases:")
        purchase_sample = purchases_df[purchases_df['LOCSTITBT'] == sample_batch][['ITEMTPCD', 'ITEMCD', 'ITEMNAME', 'BATCH NO', 'LOCSTITBT', 'IN_QTY', 'IN_RATE', 'TXDATE']]
        print(purchase_sample.to_string())
        
        print("\n\nIn Sales:")
        sales_sample = sales_df[sales_df['Batch No.'] == sample_batch][['Item Code', 'Item Name', 'Batch No.', 'Sale Qty.', 'Free Qty.', 'OUT_RATE', 'Discount Value', 'TXDATE']].head(10)
        print(sales_sample.to_string())

print("\n\n" + "=" * 80)
print("PROFIT CALCULATION REQUIREMENTS")
print("=" * 80)

print("\nFor batch-wise profit, we need:")
print("1. Purchase data: IN_QTY, IN_RATE from Purchases")
print("2. Sales data: Sale Qty., Free Qty., OUT_RATE, Discount Value from Sales")
print("3. Linking field: LOCSTITBT in Purchases = Batch No. in Sales")

print("\n\nProfit calculation per batch would be:")
print("Revenue = (Sale Qty. * OUT_RATE) - Discount Value")
print("Cost = IN_QTY * IN_RATE")
print("Loss from Free Goods = Free Qty. * OUT_RATE")
print("Profit = Revenue - Cost - Loss from Free Goods")

print("\n\nAdditional costs to consider:")
print("- SV (Service charges like insurance, freight)")
print("- CO (Cylinder charges)")
print("- CG (Other charges)")
print("These need to be allocated proportionally to FG/TR items")
