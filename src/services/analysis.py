"""Analysis service for additional reports."""
from typing import List, Dict, Tuple
from ..models.purchase import Purchase
from ..models.sale import Sale
import pandas as pd


class AnalysisService:
    """Service for additional analysis and reports."""
    
    def __init__(self, purchases: List[Purchase], sales: List[Sale]):
        """Initialize with purchases and sales data."""
        self.purchases = purchases
        self.sales = sales
        
        # Create lookups
        self.purchase_batches = set(p.batch_ref_no for p in purchases if p.batch_ref_no)
        self.sales_batches = set(s.batch_no for s in sales if s.batch_no)
    
    def get_orphan_sales(self) -> Tuple[List[Sale], List[Sale]]:
        """Get sales without matching purchase records.
        
        Returns:
            Tuple of (fg_tr_orphans, other_orphans)
        """
        fg_tr_orphans = []
        other_orphans = []
        
        for sale in self.sales:
            # Skip if has matching purchase or no batch
            if not sale.batch_no or sale.batch_no in self.purchase_batches:
                continue
            
            # Categorize
            if sale.is_tradeable:  # FG or TR
                fg_tr_orphans.append(sale)
            else:
                other_orphans.append(sale)
        
        return fg_tr_orphans, other_orphans
    
    def get_charge_items(self) -> Tuple[List[Purchase], List[Sale]]:
        """Get SV/CO/CG charge items from purchases and sales.
        
        Returns:
            Tuple of (charge_purchases, charge_sales)
        """
        charge_purchases = [p for p in self.purchases if p.is_charge]
        charge_sales = [s for s in self.sales if s.is_charge]
        
        return charge_purchases, charge_sales
    
    def get_advertising_items(self) -> Tuple[List[Purchase], List[Sale]]:
        """Get advertising items from purchases and sales.
        
        Returns:
            Tuple of (ad_purchases, ad_sales)
        """
        ad_purchases = [p for p in self.purchases if p.is_advertising]
        ad_sales = [s for s in self.sales if s.category == 'AD']
        
        return ad_purchases, ad_sales
    
    def create_orphan_sales_report(self, orphan_sales: List[Sale]) -> pd.DataFrame:
        """Create a DataFrame report for orphan sales.
        
        Args:
            orphan_sales: List of Sale objects without purchase records
            
        Returns:
            DataFrame with orphan sales details
        """
        if not orphan_sales:
            return pd.DataFrame()
        
        data = []
        for sale in orphan_sales:
            data.append({
                'batch_no': sale.batch_no,
                'item_code': sale.item_code,
                'item_name': sale.item_name,
                'category': sale.category,
                'bill_no': sale.bill_no,
                'customer_name': sale.customer_name,
                'transaction_date': sale.transaction_date.strftime('%Y-%m-%d') if sale.transaction_date else None,
                'sale_qty': sale.sale_qty,
                'free_qty': sale.free_qty,
                'out_rate': round(sale.out_rate, 2),
                'gross_value': round(sale.gross_value, 2),
                'discount_value': round(sale.discount_value, 2),
            })
        
        return pd.DataFrame(data)
    
    def create_charges_report(self) -> Dict:
        """Create summary report for charge items.
        
        Returns:
            Dictionary with charges summary
        """
        charge_purchases, charge_sales = self.get_charge_items()
        
        # Purchases by category
        purchase_summary = {}
        for p in charge_purchases:
            if p.category not in purchase_summary:
                purchase_summary[p.category] = {
                    'count': 0,
                    'total_qty': 0,
                    'total_value': 0.0,
                }
            purchase_summary[p.category]['count'] += 1
            purchase_summary[p.category]['total_qty'] += p.in_qty
            purchase_summary[p.category]['total_value'] += p.gross_value
        
        # Sales by category
        sales_summary = {}
        for s in charge_sales:
            if s.category not in sales_summary:
                sales_summary[s.category] = {
                    'count': 0,
                    'total_qty': 0,
                    'total_value': 0.0,
                }
            sales_summary[s.category]['count'] += 1
            sales_summary[s.category]['total_qty'] += s.out_qty
            sales_summary[s.category]['total_value'] += s.gross_value
        
        return {
            'purchases': purchase_summary,
            'sales': sales_summary,
            'purchase_items': charge_purchases,
            'sale_items': charge_sales,
        }
    
    def get_other_batch_purchases(self, batch_ref_no: str) -> Tuple[List[Purchase], List[Purchase]]:
        """Get all purchases for a batch, separated by FG/TR and others.
        
        Args:
            batch_ref_no: Batch reference number
            
        Returns:
            Tuple of (fg_tr_purchases, other_purchases)
        """
        fg_tr_purchases = []
        other_purchases = []
        
        for p in self.purchases:
            if p.batch_ref_no == batch_ref_no:
                if p.is_tradeable:
                    fg_tr_purchases.append(p)
                else:
                    other_purchases.append(p)
        
        return fg_tr_purchases, other_purchases
    
    def detect_anomalous_purchase_rates(self, categories: List[str] = None, threshold_pct: float = 50.0, iterations: int = 2) -> List[Dict]:
        """Detect purchase records with suspiciously low rates (< threshold % of median).
        
        This identifies potential data entry errors or internal company transfers.
        Uses iterative approach to catch cascading outliers.
        
        Args:
            categories: List of categories to analyze (default: ['FG', 'TR'])
            threshold_pct: Percentage threshold (default: 50% - flags rates less than 50% of median)
            iterations: Number of passes to detect outliers (default: 2)
            
        Returns:
            List of anomalous purchase records with details
        """
        if categories is None:
            categories = ['FG', 'TR']
        
        anomalous_records = []
        
        # Group purchases by product (item_code + item_name)
        product_purchases = {}
        for p in self.purchases:
            if p.category not in categories:
                continue
            
            key = (p.item_code, p.item_name)
            if key not in product_purchases:
                product_purchases[key] = []
            product_purchases[key].append(p)
        
        # Iterative outlier detection
        for iteration in range(iterations):
            iteration_anomalies = []
            
            for (item_code, item_name), purchases in product_purchases.items():
                # Need at least 2 purchases to compare
                if len(purchases) < 2:
                    continue
                
                # Calculate median rate (excluding already flagged anomalies)
                valid_purchases = [p for p in purchases if not any(
                    a['batch_ref_no'] == p.batch_ref_no for a in anomalous_records
                )]
                
                if len(valid_purchases) < 2:
                    continue
                
                rates = sorted([p.in_rate for p in valid_purchases])
                median_rate = rates[len(rates) // 2] if len(rates) % 2 == 1 else (rates[len(rates) // 2 - 1] + rates[len(rates) // 2]) / 2
                
                # Check each purchase against median
                for p in valid_purchases:
                    if median_rate > 0:
                        rate_pct = (p.in_rate / median_rate) * 100
                        
                        # Flag if rate is less than threshold % of median
                        if rate_pct < threshold_pct:
                            anomaly = {
                                'batch_ref_no': p.batch_ref_no,
                                'item_code': p.item_code,
                                'item_name': p.item_name,
                                'category': p.category,
                                'vendor_name': p.vendor_name,
                                'purchase_rate': p.in_rate,
                                'purchase_qty': p.in_qty,
                                'purchase_date': p.transaction_date.strftime('%Y-%m-%d') if p.transaction_date else None,
                                'median_rate': median_rate,
                                'rate_pct_of_median': rate_pct,
                                'difference_pct': 100 - rate_pct,
                                'total_batches': len(valid_purchases),
                                'iteration': iteration + 1,
                            }
                            iteration_anomalies.append(anomaly)
            
            # Add this iteration's anomalies
            anomalous_records.extend(iteration_anomalies)
            
            # If no new anomalies found, stop early
            if not iteration_anomalies:
                break
        
        # Sort by difference percentage (most anomalous first)
        anomalous_records.sort(key=lambda x: x['difference_pct'], reverse=True)
        
        return anomalous_records
    
    def get_product_wise_purchase_analysis(self, categories: List[str] = None) -> Dict:
        """Analyze purchases by product with vendor rate comparisons.
        
        Args:
            categories: List of categories to include (default: ['FG', 'TR'])
            
        Returns:
            Dictionary with product-wise analysis and vendor comparisons
        """
        if categories is None:
            categories = ['FG', 'TR']
        
        # Group purchases by product
        product_purchases = {}
        
        for p in self.purchases:
            if p.category not in categories:
                continue
            
            key = (p.item_code, p.item_name)
            if key not in product_purchases:
                product_purchases[key] = []
            product_purchases[key].append(p)
        
        # Analyze each product
        product_analysis = []
        
        for (item_code, item_name), purchases in product_purchases.items():
            # Sort purchases by rate (descending)
            sorted_purchases = sorted(purchases, key=lambda x: x.in_rate, reverse=True)
            
            # Calculate statistics
            rates = [p.in_rate for p in purchases]
            vendors = {p.vendor_name for p in purchases}
            
            min_rate = min(rates)
            max_rate = max(rates)
            avg_rate = sum(rates) / len(rates)
            rate_variance = max_rate - min_rate
            rate_variance_pct = (rate_variance / min_rate * 100) if min_rate > 0 else 0
            
            # Vendor analysis
            vendor_stats = {}
            for p in purchases:
                if p.vendor_name not in vendor_stats:
                    vendor_stats[p.vendor_name] = {
                        'rates': [],
                        'quantities': [],
                        'total_cost': 0,
                    }
                vendor_stats[p.vendor_name]['rates'].append(p.in_rate)
                vendor_stats[p.vendor_name]['quantities'].append(p.in_qty)
                vendor_stats[p.vendor_name]['total_cost'] += p.total_cost
            
            # Calculate vendor averages
            vendor_avg_rates = {}
            for vendor, stats in vendor_stats.items():
                vendor_avg_rates[vendor] = sum(stats['rates']) / len(stats['rates'])
            
            # Potential savings (if always bought at lowest rate)
            total_qty_purchased = sum(p.in_qty for p in purchases)
            actual_cost = sum(p.total_cost for p in purchases)
            potential_cost = total_qty_purchased * min_rate
            potential_savings = actual_cost - potential_cost
            
            product_analysis.append({
                'item_code': item_code,
                'item_name': item_name,
                'category': purchases[0].category,
                'total_purchases': len(purchases),
                'unique_vendors': len(vendors),
                'total_qty_purchased': total_qty_purchased,
                'min_rate': min_rate,
                'max_rate': max_rate,
                'avg_rate': avg_rate,
                'rate_variance': rate_variance,
                'rate_variance_pct': rate_variance_pct,
                'actual_cost': actual_cost,
                'potential_cost': potential_cost,
                'potential_savings': potential_savings,
                'potential_savings_pct': (potential_savings / actual_cost * 100) if actual_cost > 0 else 0,
                'purchases': sorted_purchases,
                'vendor_stats': vendor_stats,
                'vendor_avg_rates': vendor_avg_rates,
            })
        
        # Sort by rate variance (highest first) for summary
        product_analysis.sort(key=lambda x: x['rate_variance_pct'], reverse=True)
        
        return {
            'products': product_analysis,
            'total_products': len(product_analysis),
        }
    
    def get_vendor_rate_analysis(self, categories: List[str] = None) -> Dict:
        """Analyze vendors by their average rates across products.
        
        Args:
            categories: List of categories to include (default: ['FG', 'TR'])
            
        Returns:
            Dictionary with vendor analysis showing which vendors charge higher rates
        """
        if categories is None:
            categories = ['FG', 'TR']
        
        # Get product analysis first
        product_data = self.get_product_wise_purchase_analysis(categories)
        
        # Focus on products purchased from multiple vendors
        multi_vendor_products = [
            p for p in product_data['products']
            if p['unique_vendors'] > 1
        ]
        
        # Analyze vendor performance across all multi-vendor products
        vendor_performance = {}
        
        for product in multi_vendor_products:
            product_avg = product['avg_rate']
            
            for vendor, avg_rate in product['vendor_avg_rates'].items():
                if vendor not in vendor_performance:
                    vendor_performance[vendor] = {
                        'products': [],
                        'above_avg_count': 0,
                        'below_avg_count': 0,
                        'rate_diffs': [],
                    }
                
                rate_diff_pct = ((avg_rate - product_avg) / product_avg * 100) if product_avg > 0 else 0
                
                vendor_performance[vendor]['products'].append({
                    'item_name': product['item_name'],
                    'vendor_rate': avg_rate,
                    'product_avg': product_avg,
                    'diff_pct': rate_diff_pct,
                })
                vendor_performance[vendor]['rate_diffs'].append(rate_diff_pct)
                
                if avg_rate > product_avg:
                    vendor_performance[vendor]['above_avg_count'] += 1
                else:
                    vendor_performance[vendor]['below_avg_count'] += 1
        
        # Calculate vendor scores
        vendor_scores = []
        for vendor, data in vendor_performance.items():
            total_products = len(data['products'])
            avg_diff = sum(data['rate_diffs']) / len(data['rate_diffs']) if data['rate_diffs'] else 0
            above_avg_pct = (data['above_avg_count'] / total_products * 100) if total_products > 0 else 0
            
            vendor_scores.append({
                'vendor_name': vendor,
                'total_products': total_products,
                'above_avg_count': data['above_avg_count'],
                'below_avg_count': data['below_avg_count'],
                'above_avg_pct': above_avg_pct,
                'avg_rate_diff_pct': avg_diff,
                'products': data['products'],
            })
        
        # Sort by average rate difference (highest first)
        vendor_scores.sort(key=lambda x: x['avg_rate_diff_pct'], reverse=True)
        
        return {
            'vendors': vendor_scores,
            'multi_vendor_products_count': len(multi_vendor_products),
        }
