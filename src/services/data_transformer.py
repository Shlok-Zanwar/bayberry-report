"""Data transformer service to convert raw Excel data to domain models."""
import pandas as pd
from typing import List, Dict
from ..models.purchase import Purchase
from ..models.sale import Sale


class DataTransformerService:
    """Service to transform raw DataFrame data to domain models."""
    
    @staticmethod
    def transform_purchases(df: pd.DataFrame) -> List[Purchase]:
        """Transform purchases DataFrame to Purchase objects.
        
        Args:
            df: Raw purchases DataFrame from Excel
            
        Returns:
            List of Purchase objects
        """
        purchases = []
        
        for _, row in df.iterrows():
            try:
                purchase = Purchase(
                    location_code=str(row['LOCCD']) if pd.notna(row['LOCCD']) else '',
                    item_type_code=str(row['ITEMTPCD']) if pd.notna(row['ITEMTPCD']) else '',
                    item_code=str(row['ITEMCD']) if pd.notna(row['ITEMCD']) else '',
                    item_name=str(row['ITEMNAME']) if pd.notna(row['ITEMNAME']) else '',
                    batch_no=str(row['BATCH NO']) if pd.notna(row['BATCH NO']) else '',
                    batch_ref_no=str(row['BTREFNO']) if pd.notna(row['BTREFNO']) else None,
                    vendor_code=str(row['VENDORCD']) if pd.notna(row['VENDORCD']) else '',
                    vendor_name=str(row['VENDORNAME']) if pd.notna(row['VENDORNAME']) else '',
                    in_qty=int(row['IN_QTY']) if pd.notna(row['IN_QTY']) else 0,
                    # in_rate=float(row['IN_RATE']) if pd.notna(row['IN_RATE']) else 0.0,
                    in_rate=float(row['New In rate ']) if pd.notna(row['New In rate ']) else 0.0,
                    dc_qty=int(row['DCQTY']) if pd.notna(row['DCQTY']) else 0,
                    sale_qty=int(row['SALEQTY']) if pd.notna(row['SALEQTY']) else 0,
                    free_qty=int(row['FREEQTY']) if pd.notna(row['FREEQTY']) else 0,
                    basic_value=float(row['BSVAL']) if pd.notna(row['BSVAL']) else 0.0,
                    discount_value=float(row['BTDSVAL']) if pd.notna(row['BTDSVAL']) else 0.0,
                    taxable_value=float(row['BTTCVAL']) if pd.notna(row['BTTCVAL']) else 0.0,
                    gross_value=float(row['GRVAL']) if pd.notna(row['GRVAL']) else 0.0,
                    igst=float(row['IGST']) if pd.notna(row['IGST']) else 0.0,
                    cgst=float(row['CGST']) if pd.notna(row['CGST']) else 0.0,
                    sgst=float(row['SGST']) if pd.notna(row['SGST']) else 0.0,
                    transaction_date=row['TXDATE'] if pd.notna(row['TXDATE']) else None,
                    manufacture_date=str(row['MNFMMYY']) if pd.notna(row['MNFMMYY']) else None,
                    expiry_date=row['EXPMMYY'] if pd.notna(row['EXPMMYY']) else None,
                    uom_code=str(row['UOMCD']) if pd.notna(row['UOMCD']) else '',
                    hsn_code=int(row['HSNSACCD']) if pd.notna(row['HSNSACCD']) else 0,
                )
                purchases.append(purchase)
            except Exception as e:
                print(f"Warning: Failed to transform purchase row: {e}")
                continue
        
        return purchases
    
    @staticmethod
    def transform_sales(df: pd.DataFrame) -> List[Sale]:
        """Transform sales DataFrame to Sale objects.
        
        Args:
            df: Raw sales DataFrame from Excel
            
        Returns:
            List of Sale objects
        """
        sales = []
        
        for _, row in df.iterrows():
            try:
                sale = Sale(
                    location_code=str(row['LOCCD']) if pd.notna(row['LOCCD']) else '',
                    item_code=str(row['Item Code']) if pd.notna(row['Item Code']) else '',
                    item_name=str(row['Item Name']) if pd.notna(row['Item Name']) else '',
                    batch_no=str(row['Batch No.']) if pd.notna(row['Batch No.']) else None,
                    expiry_date=row['EXPMMYY'] if pd.notna(row['EXPMMYY']) else None,
                    customer_code=str(row['Cust. Code']) if pd.notna(row['Cust. Code']) else '',
                    customer_name=str(row['Customer Name']) if pd.notna(row['Customer Name']) else '',
                    bill_no=str(row['Bill No.']) if pd.notna(row['Bill No.']) else '',
                    transaction_no=str(row['Transaction No.']) if pd.notna(row['Transaction No.']) else '',
                    sale_qty=int(row['Sale Qty.']) if pd.notna(row['Sale Qty.']) else 0,
                    free_qty=int(row['Free Qty.']) if pd.notna(row['Free Qty.']) else 0,
                    out_qty=int(row['OUT_QTY']) if pd.notna(row['OUT_QTY']) else 0,
                    out_rate=float(row['OUT_RATE']) if pd.notna(row['OUT_RATE']) else 0.0,
                    basic_value=float(row['Basic Value']) if pd.notna(row['Basic Value']) else 0.0,
                    discount_value=float(row['Discount Value']) if pd.notna(row['Discount Value']) else 0.0,
                    gross_value=float(row['Gross Value']) if pd.notna(row['Gross Value']) else 0.0,
                    igst_rate=int(row['IGST RATE']) if pd.notna(row['IGST RATE']) else 0,
                    cgst_rate=int(row['CGST RATE']) if pd.notna(row['CGST RATE']) else 0,
                    sgst_rate=int(row['SGST RATE']) if pd.notna(row['SGST RATE']) else 0,
                    igst_amount=float(row['IGST Amt .']) if pd.notna(row['IGST Amt .']) else 0.0,
                    cgst_amount=float(row['CGST Amt.']) if pd.notna(row['CGST Amt.']) else 0.0,
                    sgst_amount=float(row['SGST Amt.']) if pd.notna(row['SGST Amt.']) else 0.0,
                    transaction_date=row['TXDATE'] if pd.notna(row['TXDATE']) else None,
                    division=str(row['Division']) if pd.notna(row['Division']) else '',
                    customer_type_code=str(row['CUSTTPCD']) if pd.notna(row['CUSTTPCD']) else None,
                    manager_name=str(row['MGNAME']) if pd.notna(row['MGNAME']) else None,
                    country=str(row['COUNTRY']) if pd.notna(row['COUNTRY']) else None,
                    city=str(row['CITY']) if pd.notna(row['CITY']) else None,
                    segment=str(row['Final line wise segment ']).strip() if pd.notna(row['Final line wise segment ']) else None,
                )
                sales.append(sale)
            except Exception as e:
                print(f"Warning: Failed to transform sale row: {e}")
                continue
        
        return sales
    
    @staticmethod
    def create_lookup_dicts(purchases: List[Purchase], sales: List[Sale]) -> Dict:
        """Create lookup dictionaries for efficient querying.
        
        Args:
            purchases: List of Purchase objects
            sales: List of Sale objects
            
        Returns:
            Dictionary with various lookup structures
        """
        # Purchase lookup by batch ref no
        purchase_by_batch = {}
        for p in purchases:
            if p.batch_ref_no:
                purchase_by_batch[p.batch_ref_no] = p
        
        # Sales lookup by batch no (list because multiple sales per batch)
        sales_by_batch = {}
        for s in sales:
            if s.batch_no:
                if s.batch_no not in sales_by_batch:
                    sales_by_batch[s.batch_no] = []
                sales_by_batch[s.batch_no].append(s)
        
        # All unique batch numbers
        all_batches = set(purchase_by_batch.keys()) | set(sales_by_batch.keys())
        
        return {
            'purchase_by_batch': purchase_by_batch,
            'sales_by_batch': sales_by_batch,
            'all_batches': all_batches,
            'purchases_with_ref': len(purchase_by_batch),
            'sales_with_batch': len(sales_by_batch),
            'matched_batches': len(set(purchase_by_batch.keys()) & set(sales_by_batch.keys())),
        }
