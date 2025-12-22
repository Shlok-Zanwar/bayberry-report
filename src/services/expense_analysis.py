"""Expense analysis service."""
import pandas as pd
from typing import List, Dict
from collections import defaultdict
from ..models.expense import Expense


class ExpenseAnalysisService:
    """Service for expense analysis and insights."""
    
    def __init__(self, expenses: List[Expense]):
        """Initialize with expenses data."""
        self.expenses = expenses
    
    def get_summary_stats(self) -> Dict:
        """Get overall summary statistics.
        
        Returns:
            Dictionary with overall summary
        """
        total_debit = sum(e.debit for e in self.expenses)
        total_credit = sum(e.credit for e in self.expenses)
        net_expense = total_debit - total_credit
        
        # Count transactions by type
        expense_count = sum(1 for e in self.expenses if e.is_expense)
        credit_count = sum(1 for e in self.expenses if e.is_credit)
        
        # Average per transaction
        avg_expense = total_debit / expense_count if expense_count > 0 else 0
        avg_credit = total_credit / credit_count if credit_count > 0 else 0
        
        # Date range
        dates = [e.date for e in self.expenses if e.date]
        min_date = min(dates) if dates else None
        max_date = max(dates) if dates else None
        
        return {
            'total_transactions': len(self.expenses),
            'expense_count': expense_count,
            'credit_count': credit_count,
            'total_debit': round(total_debit, 2),
            'total_credit': round(total_credit, 2),
            'net_expense': round(net_expense, 2),
            'avg_expense': round(avg_expense, 2),
            'avg_credit': round(avg_credit, 2),
            'date_range': {
                'start': min_date.strftime('%Y-%m-%d') if min_date else None,
                'end': max_date.strftime('%Y-%m-%d') if max_date else None,
            }
        }
    
    def get_group_summary(self) -> Dict:
        """Get summary by expense group (Direct/Indirect).
        
        Returns:
            Dictionary with group-wise summary
        """
        summary = defaultdict(lambda: {
            'count': 0,
            'total_debit': 0.0,
            'total_credit': 0.0,
            'net_expense': 0.0,
        })
        
        for expense in self.expenses:
            group = expense.group
            summary[group]['count'] += 1
            summary[group]['total_debit'] += expense.debit
            summary[group]['total_credit'] += expense.credit
            summary[group]['net_expense'] += expense.net_amount
        
        # Round values
        for group in summary:
            summary[group]['total_debit'] = round(summary[group]['total_debit'], 2)
            summary[group]['total_credit'] = round(summary[group]['total_credit'], 2)
            summary[group]['net_expense'] = round(summary[group]['net_expense'], 2)
        
        return dict(summary)
    
    def get_category_summary(self) -> Dict:
        """Get summary by category.
        
        Returns:
            Dictionary with category-wise summary
        """
        summary = defaultdict(lambda: {
            'count': 0,
            'total_debit': 0.0,
            'total_credit': 0.0,
            'net_expense': 0.0,
        })
        
        for expense in self.expenses:
            category = expense.category
            summary[category]['count'] += 1
            summary[category]['total_debit'] += expense.debit
            summary[category]['total_credit'] += expense.credit
            summary[category]['net_expense'] += expense.net_amount
        
        # Round and sort by net expense
        result = {}
        for category in summary:
            result[category] = {
                'count': summary[category]['count'],
                'total_debit': round(summary[category]['total_debit'], 2),
                'total_credit': round(summary[category]['total_credit'], 2),
                'net_expense': round(summary[category]['net_expense'], 2),
            }
        
        return result
    
    def get_monthly_summary(self) -> List[Dict]:
        """Get monthly expense trends.
        
        Returns:
            List of dictionaries with monthly summaries
        """
        monthly = defaultdict(lambda: {
            'month_year': '',
            'month_name': '',
            'count': 0,
            'total_debit': 0.0,
            'total_credit': 0.0,
            'net_expense': 0.0,
        })
        
        for expense in self.expenses:
            if expense.date:
                key = expense.month_year
                if not monthly[key]['month_year']:
                    monthly[key]['month_year'] = expense.month_year
                    monthly[key]['month_name'] = expense.month_name
                
                monthly[key]['count'] += 1
                monthly[key]['total_debit'] += expense.debit
                monthly[key]['total_credit'] += expense.credit
                monthly[key]['net_expense'] += expense.net_amount
        
        # Convert to list and sort by month
        result = []
        for month_data in monthly.values():
            result.append({
                'month_year': month_data['month_year'],
                'month_name': month_data['month_name'],
                'count': month_data['count'],
                'total_debit': round(month_data['total_debit'], 2),
                'total_credit': round(month_data['total_credit'], 2),
                'net_expense': round(month_data['net_expense'], 2),
            })
        
        result.sort(key=lambda x: x['month_year'])
        return result
    
    def get_top_expenses_by_particular(self, top_n: int = 20, exclude_particulars: List[str] = None) -> List[Dict]:
        """Get top expense particulars by total amount.
        
        Args:
            top_n: Number of top items to return
            exclude_particulars: List of particulars to exclude (e.g., ['Round Off'])
            
        Returns:
            List of dictionaries with particular summaries
        """
        if exclude_particulars is None:
            exclude_particulars = []
        
        particular_summary = defaultdict(lambda: {
            'particular': '',
            'count': 0,
            'total_debit': 0.0,
            'total_credit': 0.0,
            'net_expense': 0.0,
        })
        
        for expense in self.expenses:
            if expense.particulars not in exclude_particulars:
                key = expense.particulars
                particular_summary[key]['particular'] = expense.particulars
                particular_summary[key]['count'] += 1
                particular_summary[key]['total_debit'] += expense.debit
                particular_summary[key]['total_credit'] += expense.credit
                particular_summary[key]['net_expense'] += expense.net_amount
        
        # Convert to list and round
        result = []
        for item in particular_summary.values():
            result.append({
                'particular': item['particular'],
                'count': item['count'],
                'total_debit': round(item['total_debit'], 2),
                'total_credit': round(item['total_credit'], 2),
                'net_expense': round(item['net_expense'], 2),
            })
        
        # Sort by net expense (descending) and take top N
        result.sort(key=lambda x: x['net_expense'], reverse=True)
        return result[:top_n]
    
    def get_transaction_type_summary(self) -> Dict:
        """Get summary by transaction type.
        
        Returns:
            Dictionary with transaction type summary
        """
        summary = defaultdict(lambda: {
            'count': 0,
            'total_debit': 0.0,
            'total_credit': 0.0,
            'net_expense': 0.0,
        })
        
        for expense in self.expenses:
            txn_type = expense.transaction_type if expense.transaction_type else 'Unknown'
            summary[txn_type]['count'] += 1
            summary[txn_type]['total_debit'] += expense.debit
            summary[txn_type]['total_credit'] += expense.credit
            summary[txn_type]['net_expense'] += expense.net_amount
        
        # Round values
        result = {}
        for txn_type in summary:
            result[txn_type] = {
                'count': summary[txn_type]['count'],
                'total_debit': round(summary[txn_type]['total_debit'], 2),
                'total_credit': round(summary[txn_type]['total_credit'], 2),
                'net_expense': round(summary[txn_type]['net_expense'], 2),
            }
        
        return result
    
    def create_expense_dataframe(self, expenses: List[Expense] = None) -> pd.DataFrame:
        """Create a pandas DataFrame from expenses.
        
        Args:
            expenses: List of Expense objects, uses self.expenses if not provided
            
        Returns:
            DataFrame with expense details
        """
        if expenses is None:
            expenses = self.expenses
        
        data = []
        for expense in expenses:
            data.append({
                'Date': expense.date,
                'Particulars': expense.particulars,
                'Type': expense.transaction_type if expense.transaction_type else '',
                'Trans No': expense.transaction_no,
                'Narration': expense.narration,
                'Debit': expense.debit,
                'Credit': expense.credit,
                'Net Amount': expense.net_amount,
                'Group': expense.group,
                'Category': expense.category,
            })
        
        return pd.DataFrame(data)
