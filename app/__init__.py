"""Application factory for AgriSensa API."""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__, template_folder='../templates')
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from app.config.config import get_config
    app.config.from_object(get_config(config_name))
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Initialize CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=app.config['CORS_ALLOW_HEADERS'],
         methods=app.config['CORS_METHODS'])
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMP_IMAGE_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Initialize Sentry (if configured)
    if app.config.get('SENTRY_DSN'):
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0
            )
            app.logger.info("Sentry initialized successfully")
        except ImportError:
            app.logger.warning("Sentry SDK not installed. Error tracking disabled.")
    
    # CLI commands
    register_cli_commands(app)
    
    # Ensure DB tables exist at startup (Flask>=3.0 removed before_first_request)
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        app.logger.error(f"Failed to ensure DB tables exist: {e}", exc_info=True)
    
    app.logger.info(f"AgriSensa API started in {config_name} mode")
    
    return app


def setup_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # File handler
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('AgriSensa API startup')


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'success': False,
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Server Error: {error}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled Exception: {error}', exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def register_blueprints(app):
    """Register application blueprints."""
    from app.routes import (
        main_bp,
        analysis_bp,
        recommendation_bp,
        knowledge_bp,
        market_bp,
        ml_bp,
        auth_bp,
        legacy_bp
    )
    
    # Register blueprints with URL prefixes
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendation')
    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
    app.register_blueprint(market_bp, url_prefix='/api/market')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(legacy_bp, url_prefix='/api/legacy')


def register_cli_commands(app):
    """Register CLI commands."""
    
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database."""
        with app.app_context():
            db.create_all()
        app.logger.info("Database initialized successfully")
        print("✅ Database initialized successfully")
    
    @app.cli.command("seed-db")
    def seed_db_command():
        """Seed the database with sample data."""
        from app.utils.seed_data import seed_database
        with app.app_context():
            seed_database()
        app.logger.info("Database seeded successfully")
        print("✅ Database seeded successfully")
    
    @app.cli.command("create-admin")
    def create_admin_command():
        """Create an admin user."""
        from app.models.user import User
        with app.app_context():
            admin = User(
                username='admin',
                email='admin@agrisensa.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        print("✅ Admin user created: username=admin, password=admin123")
