import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.database import Asset

logger = logging.getLogger(__name__)

class AssetService:
    def update_asset(self, asset_id, user_id, **kwargs):
        asset = self.db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == user_id, Asset.is_active == True).first()
        if not asset:
            return None
        for k, v in kwargs.items():
            if hasattr(asset, k):
                setattr(asset, k, v)
        asset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete_asset(self, asset_id, user_id):
        asset = self.db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == user_id, Asset.is_active == True).first()
        if not asset:
            return False
        asset.is_active = False
        asset.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    def __init__(self, db: Session):
        self.db = db

    def add_asset(self, user_id, wallet_id, name, asset_type, symbol, quantity, buy_price):
        asset = Asset(
            user_id=user_id,
            wallet_id=wallet_id,
            name=name,
            asset_type=asset_type,
            symbol=symbol,
            quantity=quantity,
            buy_price=buy_price,
            last_price=buy_price,
            last_sync=datetime.utcnow(),
            return_value=0.0,
            return_percent=0.0,
            is_active=True
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_user_assets(self, user_id, active_only=True):
        q = self.db.query(Asset).filter(Asset.user_id == user_id)
        if active_only:
            q = q.filter(Asset.is_active == True)
        return q.order_by(Asset.name).all()

    def get_user_assets_by_type(self, user_id, asset_type, active_only=True):
        """Get user assets filtered by type (saham/kripto)"""
        q = self.db.query(Asset).filter(Asset.user_id == user_id, Asset.asset_type == asset_type)
        if active_only:
            q = q.filter(Asset.is_active == True)
        return q.order_by(Asset.name).all()

    def update_asset_price(self, asset: Asset, new_price: float):
        asset.last_price = new_price
        asset.last_sync = datetime.utcnow()
        asset.return_value = (new_price - asset.buy_price) * asset.quantity
        if asset.buy_price > 0:
            asset.return_percent = ((new_price - asset.buy_price) / asset.buy_price) * 100
        else:
            asset.return_percent = 0.0
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def sync_asset_price(self, asset: Asset):
        """Sync asset price from external API"""
        try:
            price = None
            
            # Get price based on asset type
            if asset.asset_type == 'saham':
                price = self.get_yahoo_price(asset.symbol)
            elif asset.asset_type == 'kripto':
                price = self.get_coingecko_price(asset.symbol)
            else:
                return False
                
            if price and price > 0:
                return self.update_asset_price(asset, price)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error syncing price for {asset.symbol}: {e}")
            return False

    def get_yahoo_price(self, symbol):
        """Get stock price from Yahoo Finance API"""
        try:
            # Try different symbol formats for Indonesian stocks
            symbols_to_try = [
                f"{symbol.upper()}.JK",  # Standard format
                f"{symbol.upper()}",     # Without .JK
                f"{symbol.lower()}.jk",  # Lowercase
            ]
            
            for test_symbol in symbols_to_try:
                try:
                    url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={test_symbol}'
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(url, timeout=10, headers=headers)
                    response.raise_for_status()
                    
                    data = response.json()
                    if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                        results = data['quoteResponse']['result']
                        if results and len(results) > 0:
                            result = results[0]
                            price = result.get('regularMarketPrice')
                            if price and price > 0:
                                return float(price)
                                
                except Exception as e:
                    logger.debug(f"Yahoo API failed for {test_symbol}: {e}")
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting Yahoo price for {symbol}: {e}")
            return None

    def get_coingecko_price(self, symbol):
        """Get crypto price from CoinGecko API"""
        try:
            # CoinGecko uses specific coin IDs, not symbols
            # Common mappings
            symbol_mappings = {
                'btc': 'bitcoin',
                'bitcoin': 'bitcoin',
                'eth': 'ethereum', 
                'ethereum': 'ethereum',
                'bnb': 'binancecoin',
                'binancecoin': 'binancecoin',
                'ada': 'cardano',
                'cardano': 'cardano',
                'xrp': 'ripple',
                'ripple': 'ripple',
                'sol': 'solana',
                'solana': 'solana',
                'dot': 'polkadot',
                'polkadot': 'polkadot',
                'matic': 'matic-network',
                'polygon': 'matic-network',
                'avax': 'avalanche-2',
                'avalanche': 'avalanche-2'
            }
            
            coin_id = symbol_mappings.get(symbol.lower(), symbol.lower())
            
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=idr'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if coin_id in data and 'idr' in data[coin_id]:
                price = data[coin_id]['idr']
                if price and price > 0:
                    return float(price)
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting CoinGecko price for {symbol}: {e}")
            return None

    def sync_all_user_assets(self, user_id):
        assets = self.get_user_assets(user_id)
        updated = []
        for asset in assets:
            if self.sync_asset_price(asset):
                updated.append(asset)
        return updated
