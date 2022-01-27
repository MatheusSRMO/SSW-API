from flask import Flask, request
from ssw import SSW
import json

app = Flask(__name__)

@app.route("/")
def index():
    return "welcome to ssw WebService."

@app.route("/get-drivers-list/", methods=["POST"])
def get_drivers():
    content_json = request.json
    domain, cpf, user, password = content_json["domain"], content_json["cpf"], content_json["user"], content_json["password"]
    return json.dumps(SSW(domain, cpf, user, password).get_drivers_list())


@app.route("/get-plates-list/", methods=["POST"])
def get_plates():
    content_json = request.json
    domain, cpf, user, password = content_json["domain"], content_json["cpf"], content_json["user"], content_json["password"]

    return json.dumps(SSW(domain, cpf, user, password).get_plates_list())

@app.route("/marked_notes/", methods=["POST"])
def marked_notes():
    content_json = request.json
    domain, cpf, user, password = content_json["domain"], content_json["cpf"], content_json["user"], content_json["password"]
    notes = content_json["notes"]
    
    return json.dumps(SSW(domain, cpf, user, password).marked_notes(notes))

if __name__ == "__main__":
    app.run(port=5000)