"""Market service for commodity price data."""
import random
from datetime import datetime, timedelta


class MarketService:
    """Service for market price data."""
    
    @staticmethod
    def get_current_prices(commodity):
        """Get current market prices for commodity."""
        price_db = {
            "cabai_merah_keriting": {
                "name": "Cabai Merah Keriting",
                "unit": "kg",
                "prices": {
                    "Pasar Induk": 45000,
                    "Supermarket": 55000,
                    "Ekspor": 75000
                }
            },
            "bawang_merah": {
                "name": "Bawang Merah",
                "unit": "kg",
                "prices": {
                    "Pasar Induk": 30000,
                    "Supermarket": 40000,
                    "Ekspor": 50000
                }
            }
        }
        
        price_data = price_db.get(commodity)
        if not price_data:
            return None
        
        # Add random variation (±5%)
        result = price_data.copy()
        result["prices"] = {}
        for market, base_price in price_data["prices"].items():
            variation = random.randint(-5, 5) / 100
            result["prices"][market] = int(base_price * (1 + variation))
        
        return result
    
    @staticmethod
    def get_ticker_prices():
        """Get ticker prices for multiple commodities."""
        ticker_data = {
            "cabai_merah_keriting": {"name": "Cabai Merah", "base_price": 45000, "unit": "kg"},
            "bawang_merah": {"name": "Bawang Merah", "base_price": 30000, "unit": "kg"},
            "jagung_pipilan": {"name": "Jagung Pipilan", "base_price": 5500, "unit": "kg"},
            "beras_medium": {"name": "Beras Medium", "base_price": 12000, "unit": "kg"}
        }
        
        live_data = []
        for key, value in ticker_data.items():
            variation = random.randint(-2, 2) / 100
            new_price = int(value["base_price"] * (1 + variation))
            live_data.append({
                "name": value["name"],
                "price": new_price,
                "unit": value["unit"]
            })
        
        return live_data
    
    @staticmethod
    def get_historical_prices(commodity, days):
        """Get historical price data."""
        price_db = {
            "cabai_merah_keriting": {"name": "Cabai Merah Keriting", "base_price": 45000},
            "bawang_merah": {"name": "Bawang Merah", "base_price": 30000},
            "jagung_pipilan": {"name": "Jagung Pipilan", "base_price": 5500},
            "beras_medium": {"name": "Beras Medium", "base_price": 12000}
        }
        
        base_info = price_db.get(commodity)
        if not base_info:
            return None
        
        labels = []
        prices = []
        current_price = base_info["base_price"]
        today = datetime.now()
        
        for i in range(days):
            date = today - timedelta(days=days - i - 1)
            labels.append(date.strftime('%d %b'))
            
            # Add random walk
            change_percent = random.uniform(-0.05, 0.05)
            current_price = int(current_price * (1 + change_percent))
            if current_price < 0:
                current_price = base_info["base_price"]
            
            prices.append(current_price)
        
        return {
            "labels": labels,
            "prices": prices
        }
