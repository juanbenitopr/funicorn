import json

from flask import Flask, request

app = Flask(__name__)


@app.route("/hola", methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        return request.json
    return "Works fine"

