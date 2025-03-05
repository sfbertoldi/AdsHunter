from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SECRET_KEY"] = "da80480a59b1f71b360ea403dcd0aa90"

