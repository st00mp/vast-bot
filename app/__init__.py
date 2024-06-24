from flask import Flask
from .bot import start_bot

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Default route that returns a confirmation message."""
        return "Vast Notification Bot is running!"

    # Start the bot as soon as the application is created
    start_bot()

    return app
