from backend.rest_handler.character import get_new_characters
from flask import Flask, jsonify

app = Flask(__name__)

with app.app_context():
    res = get_new_characters();
    print(res)

