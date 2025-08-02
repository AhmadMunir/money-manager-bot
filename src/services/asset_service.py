import requests
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.database import Asset

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
        # Sumber harga gratis: Yahoo Finance (saham), CoinGecko (kripto)
        if asset.asset_type == 'saham':
            price = self.get_yahoo_price(asset.symbol)
        elif asset.asset_type == 'kripto':
            price = self.get_coingecko_price(asset.symbol)
        else:
            price = None
        if price:
            return self.update_asset_price(asset, price)
        return None

    def get_yahoo_price(self, symbol):
        # Yahoo Finance API (unofficial, gratis)
        try:
            url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}.JK'
            r = requests.get(url, timeout=5)
            data = r.json()
            price = data['quoteResponse']['result'][0]['regularMarketPrice']
            return float(price)
        except Exception:
            return None

    def get_coingecko_price(self, symbol):
        # CoinGecko API (gratis, symbol: lowercase, e.g. 'btc')
        try:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=idr'
            r = requests.get(url, timeout=5)
            data = r.json()
            price = data[symbol.lower()]['idr']
            return float(price)
        except Exception:
            return None

    def sync_all_user_assets(self, user_id):
        assets = self.get_user_assets(user_id)
        updated = []
        for asset in assets:
            if self.sync_asset_price(asset):
                updated.append(asset)
        return updated
