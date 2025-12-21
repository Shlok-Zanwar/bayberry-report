"""Profit calculation model."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .purchase import Purchase
from .sale import Sale
from ..config import get_profit_share


@dataclass
class SaleDetail:
    """Detailed profit breakdown for a single sale."""
    sale: Sale
    purchase_rate: float
    
    # Calculated fields
    revenue_from_sale: float = 0.0
    cost_of_goods_sold: float = 0.0
    cost_due_to_free: float = 0.0
    cost_due_to_discount: float = 0.0
    final_profit: float = 0.0
    
    # Segment and Profit Sharing (per sale)
    segment: Optional[str] = None
    profit_share_ratio: str = "50/50"
    sz_profit_share: float = 0.0
    gz_profit_share: float = 0.0
    
    def calculate(self):
        """Calculate all profit metrics including profit shares."""
        metrics = self.sale.calculate_profit_metrics(self.purchase_rate)
        self.revenue_from_sale = metrics['revenue_from_sale']
        self.cost_of_goods_sold = metrics['cost_of_goods_sold']
        self.cost_due_to_free = metrics['cost_due_to_free']
        self.cost_due_to_discount = metrics['cost_due_to_discount']
        self.final_profit = metrics['final_profit']
        
        # Get segment from sale
        self.segment = self.sale.segment
        
        # Calculate profit shares based on this sale's segment
        share_config = get_profit_share(self.segment)
        sz_pct = share_config['SZ']
        gz_pct = share_config['GZ']
        self.profit_share_ratio = f"{sz_pct}/{gz_pct}"
        self.sz_profit_share = self.final_profit * (sz_pct / 100)
        self.gz_profit_share = self.final_profit * (gz_pct / 100)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'bill_no': self.sale.bill_no,
            'transaction_no': self.sale.transaction_no,
            'transaction_date': self.sale.transaction_date.strftime('%Y-%m-%d') if self.sale.transaction_date else None,
            'customer_name': self.sale.customer_name,
            'segment': self.segment,
            'sale_qty': self.sale.sale_qty,
            'free_qty': self.sale.free_qty,
            'out_qty': self.sale.out_qty,
            'out_rate': round(self.sale.out_rate, 2),
            'gross_value': round(self.sale.gross_value, 2),
            'discount_value': round(self.sale.discount_value, 2),
            'revenue_from_sale': round(self.revenue_from_sale, 2),
            'cost_of_goods_sold': round(self.cost_of_goods_sold, 2),
            'cost_due_to_free': round(self.cost_due_to_free, 2),
            'cost_due_to_discount': round(self.cost_due_to_discount, 2),
            'final_profit': round(self.final_profit, 2),
            'profit_share_ratio': self.profit_share_ratio,
            'sz_profit_share': round(self.sz_profit_share, 2),
            'gz_profit_share': round(self.gz_profit_share, 2),
        }


@dataclass
class BatchProfit:
    """Represents batch-wise profit calculation."""
    
    # Batch identification
    batch_ref_no: str
    item_code: str
    item_name: str
    category: str
    
    # Purchase data
    purchase: Optional[Purchase] = None
    purchase_qty: int = 0
    purchase_rate: float = 0.0
    purchase_cost: float = 0.0
    purchase_date: Optional[str] = None
    vendor_name: Optional[str] = None
    
    # Sales data (aggregated)
    sales: List[Sale] = field(default_factory=list)
    sale_details: List[SaleDetail] = field(default_factory=list)
    total_sale_qty: int = 0
    total_free_qty: int = 0
    total_out_qty: int = 0
    avg_sale_rate: float = 0.0
    
    # Revenue breakdown
    gross_revenue: float = 0.0
    discount_given: float = 0.0
    net_revenue: float = 0.0
    
    # Revenue and Cost breakdown
    revenue_from_sales: float = 0.0  # Tax-exclusive revenue from sold items
    total_cogs: float = 0.0  # Cost of goods sold (purchase_rate × total_out_qty)
    total_cost_due_to_free: float = 0.0  # For visibility (included in COGS)
    total_cost_due_to_discount: float = 0.0
    
    # Legacy fields for individual sale tracking
    total_cost_of_goods_sold: float = 0.0  # Sum from individual sales
    total_revenue_from_sales: float = 0.0  # Sum from individual sales
    
    # Final profit
    profit: float = 0.0
    profit_margin: float = 0.0
    
    # Segment and Profit Sharing
    segment: Optional[str] = None  # Dominant segment from sales
    profit_share_ratio: str = "50/50"  # SZ/GZ ratio
    sz_profit_share: float = 0.0
    gz_profit_share: float = 0.0
    
    # Status
    has_purchase: bool = False
    has_sales: bool = False
    
    def calculate(self):
        """Calculate profit and all derived metrics."""
        # Purchase metrics
        if self.purchase:
            self.has_purchase = True
            self.purchase_qty = self.purchase.in_qty
            self.purchase_rate = self.purchase.in_rate
            self.purchase_cost = self.purchase.total_cost
            self.purchase_date = self.purchase.transaction_date.strftime('%Y-%m-%d') if self.purchase.transaction_date else None
            self.vendor_name = self.purchase.vendor_name
        
        # Sales metrics (aggregate from all sales)
        if self.sales:
            self.has_sales = True
            
            # Create detailed sale breakdowns
            self.sale_details = []
            for sale in self.sales:
                sale_detail = SaleDetail(sale=sale, purchase_rate=self.purchase_rate)
                sale_detail.calculate()
                self.sale_details.append(sale_detail)
            
            # Aggregate quantities
            self.total_sale_qty = sum(s.sale_qty for s in self.sales)
            self.total_free_qty = sum(s.free_qty for s in self.sales)
            self.total_out_qty = sum(s.out_qty for s in self.sales)
            
            # Revenue calculations (keep old gross_revenue for reference)
            self.gross_revenue = sum(s.gross_value for s in self.sales)  # Includes GST
            self.discount_given = sum(s.discount_value for s in self.sales)
            self.net_revenue = self.gross_revenue - self.discount_given  # Legacy field
            
            # New tax-exclusive revenue and cost calculations
            self.revenue_from_sales = sum(sd.revenue_from_sale for sd in self.sale_details)
            self.total_cogs = self.purchase_rate * self.total_out_qty  # COGS for all outward items
            self.total_cost_due_to_free = self.purchase_rate * self.total_free_qty  # For visibility
            self.total_cost_due_to_discount = sum(sd.cost_due_to_discount for sd in self.sale_details)
            
            # Legacy fields from individual sales (for verification)
            self.total_cost_of_goods_sold = sum(sd.cost_of_goods_sold for sd in self.sale_details)
            self.total_revenue_from_sales = sum(sd.revenue_from_sale for sd in self.sale_details)
            
            # Average sale rate
            if self.total_sale_qty > 0:
                self.avg_sale_rate = self.revenue_from_sales / self.total_sale_qty
        
        # Final profit calculation: Revenue - COGS - Discount
        # Note: COGS already includes cost of free items, so we don't subtract it separately
        self.profit = self.revenue_from_sales - self.total_cogs - self.total_cost_due_to_discount
        
        # Determine dominant segment from sales (for display only)
        if self.sales:
            # Count sales by segment
            segment_counts = {}
            for sale in self.sales:
                seg = sale.segment if sale.segment else 'Unknown'
                segment_counts[seg] = segment_counts.get(seg, 0) + 1
            # Get most common segment
            self.segment = max(segment_counts, key=segment_counts.get) if segment_counts else None
        
        # Sum profit shares from individual sales (calculated per sale based on each sale's segment)
        if self.sale_details:
            self.sz_profit_share = sum(sd.sz_profit_share for sd in self.sale_details)
            self.gz_profit_share = sum(sd.gz_profit_share for sd in self.sale_details)
            # Calculate average ratio for display (weighted by profit)
            if self.profit != 0:
                sz_pct = (self.sz_profit_share / self.profit * 100) if self.profit != 0 else 50
                gz_pct = (self.gz_profit_share / self.profit * 100) if self.profit != 0 else 50
                self.profit_share_ratio = f"{sz_pct:.0f}/{gz_pct:.0f}"
            else:
                self.profit_share_ratio = "0/0"
        else:
            # No sales, use default
            self.sz_profit_share = 0.0
            self.gz_profit_share = 0.0
            self.profit_share_ratio = "0/0"
        
        # Profit margin based on tax-exclusive revenue
        if self.revenue_from_sales > 0:
            self.profit_margin = (self.profit / self.revenue_from_sales) * 100
    
    @property
    def remaining_qty(self) -> int:
        """Remaining quantity (not yet sold)."""
        return self.purchase_qty - self.total_out_qty
    
    @property
    def is_complete(self) -> bool:
        """Check if batch has both purchase and sales data."""
        return self.has_purchase and self.has_sales
    
    @property
    def status(self) -> str:
        """Get status of the batch."""
        if not self.has_purchase:
            return "No Purchase Record"
        if not self.has_sales:
            return "No Sales Yet"
        if self.remaining_qty > 0:
            return "Partial Sale"
        return "Fully Sold"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            'batch_ref_no': self.batch_ref_no,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'segment': self.segment,
            'category': self.category,
            'vendor_name': self.vendor_name,
            'purchase_date': self.purchase_date,
            'purchase_qty': self.purchase_qty,
            'purchase_rate': round(self.purchase_rate, 2),
            'purchase_cost': round(self.purchase_cost, 2),
            'total_sale_qty': self.total_sale_qty,
            'total_free_qty': self.total_free_qty,
            'total_out_qty': self.total_out_qty,
            'remaining_qty': self.remaining_qty,
            'avg_sale_rate': round(self.avg_sale_rate, 2),
            'gross_revenue': round(self.gross_revenue, 2),
            'discount_given': round(self.discount_given, 2),
            'net_revenue': round(self.net_revenue, 2),
            'revenue_from_sales': round(self.revenue_from_sales, 2),
            'total_cogs': round(self.total_cogs, 2),
            'total_cost_due_to_free': round(self.total_cost_due_to_free, 2),
            'total_cost_due_to_discount': round(self.total_cost_due_to_discount, 2),
            'profit': round(self.profit, 2),
            'profit_margin': round(self.profit_margin, 2),
            'profit_share_ratio': self.profit_share_ratio,
            'sz_profit_share': round(self.sz_profit_share, 2),
            'gz_profit_share': round(self.gz_profit_share, 2),
            'status': self.status,
            'num_sales': len(self.sale_details),
        }
