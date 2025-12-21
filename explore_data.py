import pandas as pd
import openpyxl

# Load the Excel file
file_path = 'BayberryStock.xlsx'

# First, let's see all sheet names
xl_file = pd.ExcelFile(file_path)
print("=" * 80)
print("ALL SHEETS IN THE EXCEL FILE:")
print("=" * 80)
for i, sheet in enumerate(xl_file.sheet_names, 1):
    print(f"{i}. {sheet}")

print("\n" + "=" * 80)
print("SALES SHEET ANALYSIS:")
print("=" * 80)

# Read Sales sheet (header in row 3, so skip first 2 rows)
sales_df = pd.read_excel(file_path, sheet_name='Sales', header=2)
print(f"\nShape: {sales_df.shape}")
print(f"Columns ({len(sales_df.columns)}):")
for i, col in enumerate(sales_df.columns, 1):
    print(f"  {i}. {col}")

print("\nFirst few rows:")
print(sales_df.head(10))

print("\nData types:")
print(sales_df.dtypes)

print("\nChecking Item Code patterns:")
if 'Item Code' in sales_df.columns:
    # Get first 2 characters of Item Code
    item_codes = sales_df['Item Code'].dropna().astype(str)
    print(f"\nTotal non-null Item Codes: {len(item_codes)}")
    
    # Extract first 2 characters
    first_two_chars = item_codes.str[:2].value_counts()
    print("\nItem Code prefixes (first 2 chars):")
    print(first_two_chars)
    
    # Show some examples
    print("\nSample Item Codes by prefix:")
    for prefix in ['FG', 'TR', 'SV', 'CO', 'CG', 'AD']:
        examples = item_codes[item_codes.str.startswith(prefix)].head(3)
        if len(examples) > 0:
            print(f"\n{prefix}: {list(examples.values)}")

print("\n" + "=" * 80)
print("PURCHASES SHEET ANALYSIS:")
print("=" * 80)

# Read Purchases sheet (header in row 3, so skip first 2 rows)
purchases_df = pd.read_excel(file_path, sheet_name='Purchases', header=2)
print(f"\nShape: {purchases_df.shape}")
print(f"Columns ({len(purchases_df.columns)}):")
for i, col in enumerate(purchases_df.columns, 1):
    print(f"  {i}. {col}")

print("\nFirst few rows:")
print(purchases_df.head(10))

print("\nData types:")
print(purchases_df.dtypes)

print("\nChecking Item Code patterns in Purchases:")
if 'Item Code' in purchases_df.columns:
    # Get first 2 characters of Item Code
    item_codes = purchases_df['Item Code'].dropna().astype(str)
    print(f"\nTotal non-null Item Codes: {len(item_codes)}")
    
    # Extract first 2 characters
    first_two_chars = item_codes.str[:2].value_counts()
    print("\nItem Code prefixes (first 2 chars):")
    print(first_two_chars)
    
    # Show some examples
    print("\nSample Item Codes by prefix:")
    for prefix in ['FG', 'TR', 'SV', 'CO', 'CG', 'AD']:
        examples = item_codes[item_codes.str.startswith(prefix)].head(3)
        if len(examples) > 0:
            print(f"\n{prefix}: {list(examples.values)}")

# Check for IN QTY and IN Rate columns
print("\n" + "=" * 80)
print("CHECKING KEY COLUMNS:")
print("=" * 80)

print("\nPurchases - Looking for IN QTY and IN Rate columns:")
qty_cols = [col for col in purchases_df.columns if 'qty' in col.lower() or 'quantity' in col.lower()]
rate_cols = [col for col in purchases_df.columns if 'rate' in col.lower()]
print(f"QTY related columns: {qty_cols}")
print(f"Rate related columns: {rate_cols}")

print("\nSales - Looking for Sale QTY, Free QTY, Discount columns:")
sales_qty_cols = [col for col in sales_df.columns if 'qty' in col.lower() or 'quantity' in col.lower()]
sales_discount_cols = [col for col in sales_df.columns if 'discount' in col.lower() or 'disc' in col.lower()]
sales_rate_cols = [col for col in sales_df.columns if 'rate' in col.lower()]
print(f"QTY related columns: {sales_qty_cols}")
print(f"Discount related columns: {sales_discount_cols}")
print(f"Rate related columns: {sales_rate_cols}")

# Check for Batch information
print("\n" + "=" * 80)
print("CHECKING BATCH INFORMATION:")
print("=" * 80)

print("\nPurchases - Batch columns:")
batch_cols_purchases = [col for col in purchases_df.columns if 'batch' in col.lower()]
print(f"Batch related columns: {batch_cols_purchases}")
if batch_cols_purchases:
    print(f"\nSample batch data:")
    print(purchases_df[batch_cols_purchases].head(10))

print("\nSales - Batch columns:")
batch_cols_sales = [col for col in sales_df.columns if 'batch' in col.lower()]
print(f"Batch related columns: {batch_cols_sales}")
if batch_cols_sales:
    print(f"\nSample batch data:")
    print(sales_df[batch_cols_sales].head(10))

print("\n" + "=" * 80)
print("STATISTICS:")
print("=" * 80)
print(f"\nTotal Purchases rows: {len(purchases_df)}")
print(f"Total Sales rows: {len(sales_df)}")
