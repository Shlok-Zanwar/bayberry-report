"""Sale data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Sale:
    """Represents a sale line item."""
    
    # Identifiers
    location_code: str
    item_code: str
    item_name: str
    
    # Batch information
    batch_no: Optional[str]  # Links to purchase BTREFNO
    expiry_date: Optional[datetime]
    
    # Customer information
    customer_code: str
    customer_name: str
    bill_no: str
    transaction_no: str
    
    # Quantities and Rates
    sale_qty: int  # Actual sold quantity
    free_qty: int  # Free quantity given
    out_qty: int  # Total outward quantity
    out_rate: float  # Selling rate per unit
    
    # Values
    basic_value: float
    discount_value: float  # Discount given (loss)
    gross_value: float  # Total sale value
    
    # Tax
    igst_rate: int
    cgst_rate: int
    sgst_rate: int
    igst_amount: float
    cgst_amount: float
    sgst_amount: float
    
    # Transaction details
    transaction_date: datetime
    division: str
    
    # Additional fields
    customer_type_code: Optional[str]
    manager_name: Optional[str]
    country: Optional[str]
    city: Optional[str]
    segment: Optional[str] = None  # Final line wise segment: PCD, THIRD PARTY, Internal, EXPORT
    
    def __post_init__(self):
        """Validate and process data after initialization."""
        # Extract category prefix (first 2 chars of item code)
        self.category = self.item_code[:2] if self.item_code else None
        
    @property
    def is_tradeable(self) -> bool:
        """Check if item is a tradeable product (FG or TR)."""
        return self.category in ['FG', 'TR']
    
    @property
    def is_charge(self) -> bool:
        """Check if item is a charge (SV, CO)."""
        return self.category in ['SV', 'CO']
    
    @property
    def total_qty(self) -> int:
        """Total quantity (sale + free)."""
        return self.sale_qty + self.free_qty
    
    @property
    def revenue(self) -> float:
        """Net revenue (gross - discount)."""
        return self.gross_value - self.discount_value
    
    @property
    def free_qty_loss(self) -> float:
        """Loss due to free quantity given."""
        return self.free_qty * self.out_rate
    
    @property
    def net_revenue(self) -> float:
        """Net revenue after discount and free qty loss."""
        return self.revenue - self.free_qty_loss
    
    def calculate_profit_metrics(self, purchase_rate: float) -> dict:
        """Calculate detailed profit metrics for this sale.
        
        Args:
            purchase_rate: The purchase rate from the batch
            
        Returns:
            Dictionary with profit breakdown
        """
        # Revenue from actual sales (tax-exclusive)
        revenue_from_sale = self.sale_qty * self.out_rate
        
        # Cost of goods sold (for sale qty only)
        cost_of_goods_sold = self.sale_qty * purchase_rate
        
        # Cost due to free quantity (at purchase cost) - for visibility
        cost_due_to_free = self.free_qty * purchase_rate
        
        # Cost due to discount
        cost_due_to_discount = abs(self.discount_value)
        
        # Final profit for this sale
        final_profit = revenue_from_sale - cost_of_goods_sold - cost_due_to_free - cost_due_to_discount
        
        return {
            'revenue_from_sale': revenue_from_sale,
            'cost_of_goods_sold': cost_of_goods_sold,
            'cost_due_to_free': cost_due_to_free,
            'cost_due_to_discount': cost_due_to_discount,
            'final_profit': final_profit,
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'location_code': self.location_code,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'batch_no': self.batch_no,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'customer_code': self.customer_code,
            'customer_name': self.customer_name,
            'bill_no': self.bill_no,
            'transaction_no': self.transaction_no,
            'sale_qty': self.sale_qty,
            'free_qty': self.free_qty,
            'out_qty': self.out_qty,
            'out_rate': self.out_rate,
            'basic_value': self.basic_value,
            'discount_value': self.discount_value,
            'gross_value': self.gross_value,
            'igst_rate': self.igst_rate,
            'cgst_rate': self.cgst_rate,
            'sgst_rate': self.sgst_rate,
            'igst_amount': self.igst_amount,
            'cgst_amount': self.cgst_amount,
            'sgst_amount': self.sgst_amount,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'division': self.division,
            'customer_type_code': self.customer_type_code,
            'manager_name': self.manager_name,
            'country': self.country,
            'city': self.city,
            'category': self.category,
            'segment': self.segment,
            'total_qty': self.total_qty,
            'revenue': self.revenue,
            'free_qty_loss': self.free_qty_loss,
            'net_revenue': self.net_revenue,
        }
