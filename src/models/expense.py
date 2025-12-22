"""Expense data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Expense:
    """Represents an expense transaction."""
    
    # Transaction details
    date: datetime
    particulars: str
    transaction_type: Optional[str]  # Journal, Payment BPL, Journal BPL
    transaction_no: str
    narration: str
    
    # Amounts
    debit: float  # Dr - Expense amount
    credit: float  # Cr - Credit/refund amount
    
    # Classification
    group: str  # DIRECT EXP, IN DIRECT EXP
    category: str  # PCD, OTHER(S), EXPORT, etc.
    
    def __post_init__(self):
        """Process data after initialization."""
        # Handle NaN values
        if self.debit is None or (isinstance(self.debit, float) and self.debit != self.debit):
            self.debit = 0.0
        if self.credit is None or (isinstance(self.credit, float) and self.credit != self.credit):
            self.credit = 0.0
        if self.transaction_type is None or (isinstance(self.transaction_type, float) and self.transaction_type != self.transaction_type):
            self.transaction_type = None
    
    @property
    def net_amount(self) -> float:
        """Calculate net expense (Debit - Credit)."""
        return self.debit - self.credit
    
    @property
    def is_expense(self) -> bool:
        """Check if this is an expense (Dr > 0)."""
        return self.debit > 0
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit/refund (Cr > 0)."""
        return self.credit > 0
    
    @property
    def is_direct_expense(self) -> bool:
        """Check if this is a direct expense."""
        return self.group == 'DIRECT EXP'
    
    @property
    def is_indirect_expense(self) -> bool:
        """Check if this is an indirect expense."""
        return self.group == 'IN DIRECT EXP'
    
    @property
    def month_year(self) -> str:
        """Get month-year string for grouping."""
        return self.date.strftime('%Y-%m')
    
    @property
    def month_name(self) -> str:
        """Get month name for display."""
        return self.date.strftime('%B %Y')
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date.isoformat() if self.date else None,
            'particulars': self.particulars,
            'transaction_type': self.transaction_type,
            'transaction_no': self.transaction_no,
            'narration': self.narration,
            'debit': self.debit,
            'credit': self.credit,
            'net_amount': self.net_amount,
            'group': self.group,
            'category': self.category,
            'month_year': self.month_year,
            'month_name': self.month_name,
        }
