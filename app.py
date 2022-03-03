from flask import Flask, jsonify

from models import SlurmResponse
from views import job_view, node_view

app = Flask(__name__)
app.response_class = SlurmResponse
from urls import *


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5051, debug=True)
