"""
routes/__init__.py — Blueprint registration.
"""

from flask import Flask


def register_blueprints(app: Flask):
    from routes.health import health_bp
    from routes.costs import costs_bp
    from routes.resources import resources_bp
    from routes.anomalies import anomalies_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(costs_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(anomalies_bp)
