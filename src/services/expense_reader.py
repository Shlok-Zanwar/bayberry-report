"""Expense Excel reader service."""
import pandas as pd
from typing import List
from pathlib import Path
from ..models.expense import Expense


class ExpenseReaderService:
    """Service to read and parse expense data from Excel."""
    
    def __init__(self, file_path: str):
        """Initialize with Excel file path."""
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Expense file not found: {file_path}")
        
        self._expenses_df = None
        self._expenses = None
    
    def load_data(self) -> pd.DataFrame:
        """Load expenses data from Excel.
        
        Returns:
            DataFrame with expenses data
        """
        print(f"Loading expense data from {self.file_path}...")
        
        # Read Day Wise Wokring sheet (header in row 4, skip first 3 rows)
        self._expenses_df = pd.read_excel(
            self.file_path, 
            sheet_name='Day Wise Wokring ', 
            header=3
        )
        print(f"✓ Loaded {len(self._expenses_df)} expense records")
        
        return self._expenses_df
    
    @property
    def expenses_df(self) -> pd.DataFrame:
        """Get expenses dataframe."""
        if self._expenses_df is None:
            self.load_data()
        return self._expenses_df
    
    def transform_expenses(self, df: pd.DataFrame = None) -> List[Expense]:
        """Transform expenses DataFrame to Expense objects.
        
        Args:
            df: Optional DataFrame, uses self.expenses_df if not provided
            
        Returns:
            List of Expense objects
        """
        if df is None:
            df = self.expenses_df
        
        expenses = []
        
        for _, row in df.iterrows():
            try:
                expense = Expense(
                    date=row['Date'] if pd.notna(row['Date']) else None,
                    particulars=str(row['Particulers']) if pd.notna(row['Particulers']) else '',
                    transaction_type=str(row['Type']) if pd.notna(row['Type']) else None,
                    transaction_no=str(row['Trans no']) if pd.notna(row['Trans no']) else '',
                    narration=str(row['Narration']) if pd.notna(row['Narration']) else '',
                    debit=float(row['Dr']) if pd.notna(row['Dr']) else 0.0,
                    credit=float(row['cr']) if pd.notna(row['cr']) else 0.0,
                    group=str(row['Group']) if pd.notna(row['Group']) else '',
                    category=str(row['Category']) if pd.notna(row['Category']) else '',
                )
                expenses.append(expense)
            except Exception as e:
                print(f"Warning: Failed to transform expense row: {e}")
                continue
        
        self._expenses = expenses
        return expenses
    
    @property
    def expenses(self) -> List[Expense]:
        """Get list of Expense objects."""
        if self._expenses is None:
            self.transform_expenses()
        return self._expenses
    
    def get_summary(self) -> dict:
        """Get summary statistics of the expense data."""
        df = self.expenses_df
        
        total_debit = df['Dr'].sum() if 'Dr' in df.columns else 0
        total_credit = df['cr'].sum() if 'cr' in df.columns else 0
        
        return {
            'total_records': len(df),
            'total_debit': total_debit,
            'total_credit': total_credit,
            'net_expense': total_debit - total_credit,
            'date_range': {
                'start': df['Date'].min().strftime('%Y-%m-%d') if pd.notna(df['Date'].min()) else None,
                'end': df['Date'].max().strftime('%Y-%m-%d') if pd.notna(df['Date'].max()) else None,
            },
            'groups': df['Group'].value_counts().to_dict() if 'Group' in df.columns else {},
            'categories': df['Category'].value_counts().to_dict() if 'Category' in df.columns else {},
            'transaction_types': df['Type'].value_counts().to_dict() if 'Type' in df.columns else {},
        }
