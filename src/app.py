"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_jwt_extended import JWTManager


ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "../public/"
)
app = Flask(__name__)
app.url_map.strict_slashes = False

# database configuration
db_url = os.getenv("DATABASE_URL")
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://doadmin:AVNS_31pfFnoUGUTUvkjiDQQ@dbaas-db-8958271-do-user-13342923-0.b.db.ondigitalocean.com:25060/defaultdb"
if db_url is not None:

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
    app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://doadmin:AVNS_31pfFnoUGUTUvkjiDQQ@dbaas-db-8958271-do-user-13342923-0.b.db.ondigitalocean.com:25060/defaultdb"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
    app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://doadmin:AVNS_31pfFnoUGUTUvkjiDQQ@dbaas-db-8958271-do-user-13342923-0.b.db.ondigitalocean.com:25060/defaultdb"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# Configura la extensión Flask-JWT-Extended
app.config["JWT_SECRET_KEY"] = "franpablodonato"
# app.config["JWT_HEADER_TYPE"] = "Bearer"
# app.config['PROPAGATE_EXCEPTIONS'] = True
jwt = JWTManager(app)
# jwt_m.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix="/api")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
@app.route("/")
def sitemap():
    return generate_sitemap(app)


# any other endpoint will try to serve it like a static file
@app.route("/<path:path>", methods=["GET"])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = "index.html"
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


# this only runs if `$ python src/main.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3001))
    app.run_server(host="0.0.0.0", port=PORT, debug=False)
