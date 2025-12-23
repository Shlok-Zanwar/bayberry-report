"""Configuration file for profit sharing and other settings."""

# Profit Sharing Configuration
# 
# Easy to modify - just change the percentages here
# Each segment has its own SZ/GZ profit share ratio
# The percentages should add up to 100 for each segment
#
# Segments:
#   - PCD: Personal Care & Cosmetics Distribution
#   - THIRD PARTY: Third party sales
#   - Internal: Internal transfers
#   - EXPORT: Export sales

PROFIT_SHARE_CONFIG = {
    'PCD': {
        'SZ': 67,  # SZ gets 66%
        'GZ': 33,  # GZ gets 34%
    },
    'THIRD PARTY': {
        'SZ': 97,  # SZ gets 97%
        'GZ': 3,  # GZ gets 3%
    },
    'Internal': {
        'SZ': 50,  # SZ gets 50%
        'GZ': 50,  # GZ gets 50%
    },
    'EXPORT': {
        'SZ': 97,  # SZ gets 97%
        'GZ': 3,  # GZ gets 3%
    },
}

# Default profit share if segment is unknown or missing
DEFAULT_PROFIT_SHARE = {
    'SZ': 50,
    'GZ': 50,
}


def get_profit_share(segment: str = None) -> dict:
    """Get profit share percentages for a segment.
    
    Args:
        segment: The sales segment (PCD, THIRD PARTY, Internal, EXPORT)
        
    Returns:
        Dictionary with SZ and GZ percentages
    """
    if segment and segment in PROFIT_SHARE_CONFIG:
        return PROFIT_SHARE_CONFIG[segment]
    return DEFAULT_PROFIT_SHARE


def validate_profit_shares():
    """Validate that all profit shares add up to 100%."""
    errors = []
    for segment, shares in PROFIT_SHARE_CONFIG.items():
        total = shares.get('SZ', 0) + shares.get('GZ', 0)
        if total != 100:
            errors.append(f"Segment '{segment}': shares total {total}% (should be 100%)")
    
    if errors:
        raise ValueError("Profit share configuration errors:\n" + "\n".join(errors))
    
    return True
