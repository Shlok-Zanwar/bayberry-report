"""Excel reader service to load and parse data from Excel file."""
import pandas as pd
from typing import Tuple
from pathlib import Path


class ExcelReaderService:
    """Service to read and parse Excel data."""
    
    def __init__(self, file_path: str):
        """Initialize with Excel file path."""
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        self._purchases_df = None
        self._sales_df = None
    
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load both Purchases and Sales sheets from Excel.
        
        Returns:
            Tuple of (purchases_df, sales_df)
        """
        print(f"Loading data from {self.file_path}...")
        
        # Read Purchases sheet (header in row 3, skip first 2 rows)
        self._purchases_df = pd.read_excel(
            self.file_path, 
            sheet_name='Purchases', 
            header=2
        )
        print(f"✓ Loaded {len(self._purchases_df)} purchase records")
        
        # Read Sales sheet (header in row 3, skip first 2 rows)
        self._sales_df = pd.read_excel(
            self.file_path, 
            sheet_name='Sales', 
            header=2
        )
        print(f"✓ Loaded {len(self._sales_df)} sale records")
        
        return self._purchases_df, self._sales_df
    
    @property
    def purchases_df(self) -> pd.DataFrame:
        """Get purchases dataframe."""
        if self._purchases_df is None:
            self.load_data()
        return self._purchases_df
    
    @property
    def sales_df(self) -> pd.DataFrame:
        """Get sales dataframe."""
        if self._sales_df is None:
            self.load_data()
        return self._sales_df
    
    def get_summary(self) -> dict:
        """Get summary statistics of the data."""
        purchases_df = self.purchases_df
        sales_df = self.sales_df
        
        return {
            'total_purchases': len(purchases_df),
            'total_sales': len(sales_df),
            'purchase_categories': purchases_df['ITEMTPCD'].value_counts().to_dict(),
            'sales_categories': sales_df['Item Code'].str[:2].value_counts().to_dict(),
            'date_range_purchases': {
                'start': purchases_df['TXDATE'].min().strftime('%Y-%m-%d') if pd.notna(purchases_df['TXDATE'].min()) else None,
                'end': purchases_df['TXDATE'].max().strftime('%Y-%m-%d') if pd.notna(purchases_df['TXDATE'].max()) else None,
            },
            'date_range_sales': {
                'start': sales_df['TXDATE'].min().strftime('%Y-%m-%d') if pd.notna(sales_df['TXDATE'].min()) else None,
                'end': sales_df['TXDATE'].max().strftime('%Y-%m-%d') if pd.notna(sales_df['TXDATE'].max()) else None,
            },
        }
