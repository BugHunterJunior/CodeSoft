from flask import Flask
import config
import database
from auth  import auth
from tasks import tasks
from api   import api


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG

    # Initialise database helpers
    database.init_app(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(tasks)
    app.register_blueprint(api)

    # Create tables on first run (inside an app context)
    with app.app_context():
        database.init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
