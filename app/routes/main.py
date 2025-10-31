"""Main routes for AgriSensa API."""
from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Render the main dashboard page."""
    return render_template('index.html')


@main_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'AgriSensa API is running'
    }), 200


@main_bp.route('/api/info')
def api_info():
    """API information endpoint."""
    return jsonify({
        'success': True,
        'api_name': 'AgriSensa API',
        'version': '2.0.0',
        'description': 'Smart Agriculture Platform for Indonesian Farmers',
        'endpoints': {
            'auth': '/api/auth',
            'analysis': '/api/analysis',
            'recommendation': '/api/recommendation',
            'knowledge': '/api/knowledge',
            'market': '/api/market',
            'ml': '/api/ml'
        }
    }), 200


@main_bp.route('/test')
def test_page():
    """Render test page for debugging."""
    return render_template('test.html')
