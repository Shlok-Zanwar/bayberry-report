"""Purchase data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Purchase:
    """Represents a purchase line item."""
    
    # Identifiers
    location_code: str
    item_type_code: str  # FG, TR, SV, CO, CG, AD
    item_code: str
    item_name: str
    
    # Batch information
    batch_no: str  # Internal batch number
    batch_ref_no: Optional[str]  # Reference batch number (links to sales)
    
    # Vendor information
    vendor_code: str
    vendor_name: str
    
    # Quantities and Rates
    in_qty: int  # Final billed quantity
    in_rate: float  # Final billed rate
    dc_qty: int  # Delivery challan quantity
    sale_qty: int  # Sale quantity
    free_qty: int  # Free quantity
    
    # Values
    basic_value: float  # BSVAL
    discount_value: float  # BTDSVAL
    taxable_value: float  # BTTCVAL
    gross_value: float  # GRVAL
    
    # Tax
    igst: float
    cgst: float
    sgst: float
    
    # Dates
    transaction_date: datetime
    purchase_date: Optional[datetime]  # PODT column
    manufacture_date: Optional[str]
    expiry_date: Optional[datetime]
    
    # Additional fields
    uom_code: str  # Unit of measurement
    hsn_code: int
    
    def __post_init__(self):
        """Validate and process data after initialization."""
        # Extract category prefix (first 2 chars of item type)
        self.category = self.item_type_code[:2] if self.item_type_code else None
        
    @property
    def is_tradeable(self) -> bool:
        """Check if item is a tradeable product (FG or TR)."""
        return self.category in ['FG', 'TR']
    
    @property
    def is_charge(self) -> bool:
        """Check if item is a charge (SV, CO, CG)."""
        return self.category in ['SV', 'CO', 'CG']
    
    @property
    def is_advertising(self) -> bool:
        """Check if item is advertising/promotional."""
        return self.category == 'AD'
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost of purchase."""
        return self.in_qty * self.in_rate
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'location_code': self.location_code,
            'item_type_code': self.item_type_code,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'batch_no': self.batch_no,
            'batch_ref_no': self.batch_ref_no,
            'vendor_code': self.vendor_code,
            'vendor_name': self.vendor_name,
            'in_qty': self.in_qty,
            'in_rate': self.in_rate,
            'dc_qty': self.dc_qty,
            'sale_qty': self.sale_qty,
            'free_qty': self.free_qty,
            'basic_value': self.basic_value,
            'discount_value': self.discount_value,
            'taxable_value': self.taxable_value,
            'gross_value': self.gross_value,
            'igst': self.igst,
            'cgst': self.cgst,
            'sgst': self.sgst,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'manufacture_date': self.manufacture_date,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'uom_code': self.uom_code,
            'hsn_code': self.hsn_code,
            'category': self.category,
            'total_cost': self.total_cost,
        }
