"""Profit calculation service."""
from typing import List, Dict
from ..models.purchase import Purchase
from ..models.sale import Sale
from ..models.profit import BatchProfit


class ProfitCalculatorService:
    """Service to calculate batch-wise profit."""
    
    def __init__(self, purchases: List[Purchase], sales: List[Sale]):
        """Initialize with purchases and sales data."""
        self.purchases = purchases
        self.sales = sales
        
        # Create lookups
        self.purchase_by_batch = {}
        for p in purchases:
            if p.batch_ref_no:
                self.purchase_by_batch[p.batch_ref_no] = p
        
        self.sales_by_batch = {}
        for s in sales:
            if s.batch_no:
                if s.batch_no not in self.sales_by_batch:
                    self.sales_by_batch[s.batch_no] = []
                self.sales_by_batch[s.batch_no].append(s)
        
        # Get all unique batches
        self.all_batches = set(self.purchase_by_batch.keys()) | set(self.sales_by_batch.keys())
    
    def calculate_batch_profits(self, include_categories: List[str] = None) -> List[BatchProfit]:
        """Calculate profit for all batches.
        
        Args:
            include_categories: List of categories to include (e.g., ['FG', 'TR'])
                               If None, includes FG and TR by default
        
        Returns:
            List of BatchProfit objects
        """
        if include_categories is None:
            include_categories = ['FG', 'TR']  # Default to tradeable items only
        
        batch_profits = []
        
        for batch_ref_no in self.all_batches:
            # Get purchase and sales for this batch
            purchase = self.purchase_by_batch.get(batch_ref_no)
            sales = self.sales_by_batch.get(batch_ref_no, [])
            
            # Determine category and item info
            if purchase:
                category = purchase.category
                item_code = purchase.item_code
                item_name = purchase.item_name
            elif sales:
                category = sales[0].category
                item_code = sales[0].item_code
                item_name = sales[0].item_name
            else:
                continue
            
            # Filter by category
            if category not in include_categories:
                continue
            
            # Create BatchProfit object
            batch_profit = BatchProfit(
                batch_ref_no=batch_ref_no,
                item_code=item_code,
                item_name=item_name,
                category=category,
                purchase=purchase,
                sales=sales,
            )
            
            # Calculate all metrics
            batch_profit.calculate()
            
            batch_profits.append(batch_profit)
        
        return batch_profits
    
    def get_summary_by_category(self, batch_profits: List[BatchProfit]) -> Dict:
        """Get summary statistics by category.
        
        Args:
            batch_profits: List of BatchProfit objects
            
        Returns:
            Dictionary with summary by category
        """
        summary = {}
        
        for bp in batch_profits:
            if bp.category not in summary:
                summary[bp.category] = {
                    'total_batches': 0,
                    'total_purchase_cost': 0.0,
                    'total_revenue': 0.0,
                    'total_profit': 0.0,
                    'avg_profit_margin': 0.0,
                    'batches_with_profit': 0,
                    'batches_with_loss': 0,
                }
            
            summary[bp.category]['total_batches'] += 1
            summary[bp.category]['total_purchase_cost'] += bp.purchase_cost
            summary[bp.category]['total_revenue'] += bp.revenue_from_sales
            summary[bp.category]['total_profit'] += bp.profit
            
            if bp.profit > 0:
                summary[bp.category]['batches_with_profit'] += 1
            else:
                summary[bp.category]['batches_with_loss'] += 1
        
        # Calculate average profit margin
        for cat in summary:
            if summary[cat]['total_revenue'] > 0:
                summary[cat]['avg_profit_margin'] = (
                    summary[cat]['total_profit'] / summary[cat]['total_revenue'] * 100
                )
        
        return summary
    
    def get_summary_stats(self, batch_profits: List[BatchProfit]) -> Dict:
        """Get overall summary statistics.
        
        Args:
            batch_profits: List of BatchProfit objects
            
        Returns:
            Dictionary with overall summary
        """
        total_batches = len(batch_profits)
        total_purchase_cost = sum(bp.purchase_cost for bp in batch_profits)
        total_revenue = sum(bp.revenue_from_sales for bp in batch_profits)
        total_profit = sum(bp.profit for bp in batch_profits)
        
        batches_with_profit = sum(1 for bp in batch_profits if bp.profit > 0)
        batches_with_loss = sum(1 for bp in batch_profits if bp.profit < 0)
        batches_breakeven = total_batches - batches_with_profit - batches_with_loss
        
        avg_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
        
        return {
            'total_batches': total_batches,
            'total_purchase_cost': round(total_purchase_cost, 2),
            'total_revenue': round(total_revenue, 2),
            'total_profit': round(total_profit, 2),
            'avg_profit_margin': round(avg_profit_margin, 2),
            'batches_with_profit': batches_with_profit,
            'batches_with_loss': batches_with_loss,
            'batches_breakeven': batches_breakeven,
        }
