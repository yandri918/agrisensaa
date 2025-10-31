"""API routes/blueprints for AgriSensa API."""
from app.routes.main import main_bp
from app.routes.analysis import analysis_bp
from app.routes.recommendation import recommendation_bp
from app.routes.knowledge import knowledge_bp
from app.routes.market import market_bp
from app.routes.ml import ml_bp
from app.routes.auth import auth_bp
from app.routes.legacy import legacy_bp

__all__ = [
    'main_bp',
    'analysis_bp',
    'recommendation_bp',
    'knowledge_bp',
    'market_bp',
    'ml_bp',
    'auth_bp',
    'legacy_bp'
]
