"""
Main Application Entry Point

Architectural Intent:
- Initialize the Flask web application
- Register all API routes
- Configure application settings
- Serve as the entry point for the presentation layer

Key Design Decisions:
1. Uses Flask as the web framework for API implementation
2. All routes are registered through the controller modules
3. Application configuration is minimal for the MVP
4. Follows standard Flask application structure
"""

from flask import Flask
import os
import sys
import os.path

# Add the project root to the Python path to enable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from presentation.api.code_review_controller import setup_routes


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-ecrp')
    
    # Register routes
    setup_routes(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'ECRP API'}, 200
    
    # Serve the UI
    @app.route('/')
    def index():
        from flask import send_file
        import os
        ui_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'presentation', 'ui', 'index.html')
        return send_file(ui_path)
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)