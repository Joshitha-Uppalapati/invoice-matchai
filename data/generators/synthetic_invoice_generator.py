"""
Synthetic Freight Invoice Generator
Generates realistic freight invoices with intentional billing errors for audit testing.

Features:
- Real ZIP code pairs with calculated distances
- Carrier-specific rate structures (FedEx, UPS, Regional carriers)
- Seasonal pricing patterns (Q4 peak, fuel surcharges)
- Realistic accessorial charges
- Intentional errors (5-10% of invoices)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import hashlib


class FreightInvoiceGenerator:
    """Generate realistic synthetic freight invoices with billing errors."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Real US ZIP codes for major metros (origin/destination pairs)
        self.zip_codes = {
            'NYC': ['10001', '10002', '10003', '10011', '10013'],
            'LA': ['90001', '90002', '90005', '90011', '90013'],
            'Chicago': ['60601', '60602', '60603', '60604', '60605'],
            'Houston': ['77001', '77002', '77003', '77004', '77005'],
            'Phoenix': ['85001', '85003', '85004', '85006', '85007'],
            'Philadelphia': ['19101', '19102', '19103', '19104', '19106'],
            'San Antonio': ['78201', '78202', '78203', '78204', '78205'],
            'San Diego': ['92101', '92102', '92103', '92104', '92105'],
            'Dallas': ['75201', '75202', '75203', '75204', '75205'],
            'Miami': ['33101', '33125', '33126', '33127', '33128']
        }
        
        # Carriers with their base rate characteristics
        self.carriers = {
            'FedEx Ground': {'base_rate_per_mile': 0.85, 'min_charge': 45, 'fuel_base': 0.12},
            'UPS Ground': {'base_rate_per_mile': 0.82, 'min_charge': 42, 'fuel_base': 0.115},
            'XPO Logistics': {'base_rate_per_mile': 0.75, 'min_charge': 38, 'fuel_base': 0.11},
            'Old Dominion': {'base_rate_per_mile': 0.78, 'min_charge': 40, 'fuel_base': 0.108},
            'YRC Freight': {'base_rate_per_mile': 0.72, 'min_charge': 36, 'fuel_base': 0.105},
        }
        
        # Distance matrix (approximate miles between cities)
        self.distances = {
            ('NYC', 'LA'): 2789,
            ('NYC', 'Chicago'): 789,
            ('NYC', 'Houston'): 1628,
            ('LA', 'Phoenix'): 373,
            ('Chicago', 'Dallas'): 967,
            ('Houston', 'Miami'): 1187,
            ('Philadelphia', 'San Diego'): 2707,
            ('San Antonio', 'Phoenix'): 842,
            ('Dallas', 'Miami'): 1302,
            ('NYC', 'Miami'): 1280,
        }
        
        # Accessorial services with rates
        self.accessorials = {
            'liftgate_pickup': 75,
            'liftgate_delivery': 75,
            'residential_delivery': 95,
            'inside_delivery': 125,
            'appointment_delivery': 50,
            'limited_access': 85,
            'notification_prior': 25,
        }
        
    def _get_distance(self, origin_city: str, dest_city: str) -> int:
        """Get distance between cities, with some variation."""
        key = (origin_city, dest_city)
        reverse_key = (dest_city, origin_city)
        
        if key in self.distances:
            base_distance = self.distances[key]
        elif reverse_key in self.distances:
            base_distance = self.distances[reverse_key]
        else:
            # Random distance for pairs not in matrix
            base_distance = random.randint(300, 2500)
        
        # Add +/- 5% variation for different routes
        variation = random.uniform(0.95, 1.05)
        return int(base_distance * variation)
    
    def _calculate_fuel_surcharge(self, date: datetime, base_rate: float, carrier: str) -> float:
        """Calculate fuel surcharge based on date and carrier."""
        fuel_base = self.carriers[carrier]['fuel_base']
        
        # Higher fuel costs in 2024 Q4
        if date.month in [10, 11, 12]:
            fuel_multiplier = random.uniform(1.15, 1.25)
        else:
            fuel_multiplier = random.uniform(1.0, 1.1)
        
        return fuel_base * fuel_multiplier
    
    def _generate_shipment_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Generate random shipment date with weekday bias."""
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        date = start_date + timedelta(days=random_days)
        
        # Bias towards weekdays (less weekend shipping)
        if date.weekday() >= 5:  # Saturday or Sunday
            if random.random() > 0.3:  # 70% chance to move to weekday
                date += timedelta(days=(7 - date.weekday()))
        
        return date
    
    def _select_accessorials(self, is_residential: bool) -> List[str]:
        """Select realistic accessorial services."""
        services = []
        
        # Residential deliveries more likely to need liftgate
        if is_residential:
            if random.random() < 0.6:
                services.append('residential_delivery')
            if random.random() < 0.4:
                services.append('liftgate_delivery')
        else:
            if random.random() < 0.15:
                services.append('liftgate_delivery')
        
        # Other services
        if random.random() < 0.1:
            services.append('inside_delivery')
        if random.random() < 0.2:
            services.append('appointment_delivery')
        if random.random() < 0.08:
            services.append('limited_access')
        
        return services
    
    def _introduce_billing_error(self, invoice: Dict, error_type: str) -> Dict:
        """Introduce intentional billing error."""
        
        if error_type == 'underbilled_linehaul':
            # Reduce linehaul by 10-30%
            reduction = random.uniform(0.10, 0.30)
            invoice['actual_billed_linehaul'] *= (1 - reduction)
            invoice['error_injected'] = 'underbilled_linehaul'
            invoice['error_amount'] = invoice['expected_linehaul'] - invoice['actual_billed_linehaul']
        
        elif error_type == 'missing_fuel_surcharge':
            # Don't bill fuel surcharge
            invoice['actual_billed_fuel'] = 0
            invoice['error_injected'] = 'missing_fuel_surcharge'
            invoice['error_amount'] = invoice['expected_fuel_surcharge']
        
        elif error_type == 'incorrect_fuel_rate':
            # Use wrong fuel rate (lower)
            wrong_rate = invoice['expected_fuel_surcharge'] * random.uniform(0.5, 0.8)
            invoice['actual_billed_fuel'] = wrong_rate
            invoice['error_injected'] = 'incorrect_fuel_rate'
            invoice['error_amount'] = invoice['expected_fuel_surcharge'] - wrong_rate
        
        elif error_type == 'missing_accessorial':
            # Don't bill one of the accessorials
            if invoice['accessorial_services']:
                services_list = invoice['accessorial_services'].split(',') if isinstance(invoice['accessorial_services'], str) else invoice['accessorial_services']
                if services_list and services_list[0]:  # Make sure list is not empty
                    service = random.choice(services_list)
                    charge = self.accessorials[service]
                    invoice['actual_billed_accessorials'] -= charge
                    invoice['error_injected'] = f'missing_accessorial_{service}'
                    invoice['error_amount'] = charge
        
        elif error_type == 'wrong_residential_flag':
            # Bill as commercial when it's residential
            if invoice['is_residential']:
                invoice['actual_billed_accessorials'] -= 95  # residential fee
                invoice['error_injected'] = 'wrong_residential_flag'
                invoice['error_amount'] = 95
        
        # Recalculate total
        invoice['actual_total_billed'] = (
            invoice['actual_billed_linehaul'] + 
            invoice['actual_billed_fuel'] + 
            invoice['actual_billed_accessorials']
        )
        
        return invoice
    
    def generate_invoices(
        self, 
        n: int = 10000,
        start_date: datetime = None,
        end_date: datetime = None,
        error_rate: float = 0.08  # 8% of invoices have errors
    ) -> pd.DataFrame:
        """Generate n synthetic freight invoices."""
        
        if start_date is None:
            start_date = datetime(2024, 1, 1)
        if end_date is None:
            end_date = datetime(2024, 12, 31)
        
        invoices = []
        
        for i in range(n):
            # Select random origin/destination
            origin_city = random.choice(list(self.zip_codes.keys()))
            dest_city = random.choice([c for c in self.zip_codes.keys() if c != origin_city])
            
            origin_zip = random.choice(self.zip_codes[origin_city])
            dest_zip = random.choice(self.zip_codes[dest_city])
            
            # Select carrier and shipment details
            carrier = random.choice(list(self.carriers.keys()))
            distance = self._get_distance(origin_city, dest_city)
            weight = random.randint(50, 5000)  # lbs
            shipment_date = self._generate_shipment_date(start_date, end_date)
            is_residential = random.random() < 0.3  # 30% residential
            
            # Calculate expected charges
            carrier_config = self.carriers[carrier]
            base_rate = max(
                distance * carrier_config['base_rate_per_mile'],
                carrier_config['min_charge']
            )
            
            # Weight-based adjustment
            if weight > 2000:
                base_rate *= 1.15
            elif weight < 200:
                base_rate *= 1.2
            
            fuel_rate = self._calculate_fuel_surcharge(shipment_date, base_rate, carrier)
            fuel_charge = base_rate * fuel_rate
            
            # Accessorials
            accessorial_services = self._select_accessorials(is_residential)
            accessorial_total = sum(self.accessorials[s] for s in accessorial_services)
            
            expected_total = base_rate + fuel_charge + accessorial_total
            
            # Create invoice
            invoice_id = hashlib.md5(f"{i}_{shipment_date}_{carrier}".encode()).hexdigest()[:12].upper()
            
            invoice = {
                'invoice_id': invoice_id,
                'shipment_date': shipment_date.strftime('%Y-%m-%d'),
                'carrier': carrier,
                'origin_zip': origin_zip,
                'dest_zip': dest_zip,
                'origin_city': origin_city,
                'dest_city': dest_city,
                'distance_miles': distance,
                'weight_lbs': weight,
                'is_residential': is_residential,
                'accessorial_services': ','.join(accessorial_services) if accessorial_services else '',
                
                # Expected charges (what SHOULD be billed)
                'expected_linehaul': round(base_rate, 2),
                'expected_fuel_surcharge': round(fuel_charge, 2),
                'expected_fuel_rate_pct': round(fuel_rate * 100, 2),
                'expected_accessorials': round(accessorial_total, 2),
                'expected_total': round(expected_total, 2),
                
                # Actual charges (what WAS billed) - initially same as expected
                'actual_billed_linehaul': round(base_rate, 2),
                'actual_billed_fuel': round(fuel_charge, 2),
                'actual_billed_accessorials': round(accessorial_total, 2),
                'actual_total_billed': round(expected_total, 2),
                
                'error_injected': 'none',
                'error_amount': 0.0
            }
            
            # Introduce errors in some invoices
            if random.random() < error_rate:
                error_types = [
                    'underbilled_linehaul',
                    'missing_fuel_surcharge', 
                    'incorrect_fuel_rate',
                    'missing_accessorial',
                    'wrong_residential_flag'
                ]
                
                # Weight error types (some more common)
                weights = [0.35, 0.25, 0.20, 0.15, 0.05]
                error_type = random.choices(error_types, weights=weights)[0]
                
                invoice = self._introduce_billing_error(invoice, error_type)
            
            invoices.append(invoice)
        
        df = pd.DataFrame(invoices)
        
        # Add calculated columns
        df['leakage_amount'] = df['expected_total'] - df['actual_total_billed']
        df['leakage_pct'] = (df['leakage_amount'] / df['expected_total'] * 100).round(2)
        df['has_leakage'] = df['leakage_amount'] > 1.0  # $1 threshold
        
        return df


def main():
    """Generate dataset and save to CSV."""
    print("🚚 Generating 10,000 synthetic freight invoices...")
    
    generator = FreightInvoiceGenerator(seed=42)
    df = generator.generate_invoices(n=10000, error_rate=0.08)
    
    # Save to CSV
    output_file = 'freight_invoices_10k.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✅ Generated {len(df)} invoices")
    print(f"📊 Dataset saved to: {output_file}")
    print(f"\n📈 DATASET STATISTICS:")
    print(f"   Total freight spend: ${df['actual_total_billed'].sum():,.2f}")
    print(f"   Invoices with errors: {df['has_leakage'].sum()} ({df['has_leakage'].mean()*100:.1f}%)")
    print(f"   Total leakage: ${df['leakage_amount'].sum():,.2f}")
    print(f"   Average leakage per flagged invoice: ${df[df['has_leakage']]['leakage_amount'].mean():.2f}")
    print(f"\n🔍 ERROR BREAKDOWN:")
    print(df[df['error_injected'] != 'none']['error_injected'].value_counts())
    print(f"\n💰 TOP 5 LEAKAGE INVOICES:")
    print(df.nlargest(5, 'leakage_amount')[['invoice_id', 'carrier', 'distance_miles', 'actual_total_billed', 'leakage_amount', 'error_injected']])


if __name__ == '__main__':
    main()
