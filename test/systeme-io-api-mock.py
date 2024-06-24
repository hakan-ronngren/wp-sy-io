#!/usr/bin/env python3

from flask import Flask, request, jsonify

import time

app = Flask(__name__)

contacts = []
latest_contact_id = 0

tags = [
    {'id': 1, 'name': 'tag1'},
    {'id': 2, 'name': 'tag2'},
    {'id': 3, 'name': 'tag3'}
]

@app.route('/')
def root():
    log_request()

    return log_result(jsonify({'result': 'OK'}), 200)

@app.route('/test/reset', methods=['POST'])
def reset():
    log_request()

    global contacts
    global latest_contact_id
    contacts = []
    latest_contact_id = 0
    return log_result(jsonify({'result': 'OK'}), 204)

@app.route('/api/contacts', methods=['POST'])
def subscribe():
    log_request()

    global latest_contact_id
    global contacts

    api_key = request.headers.get('X-Api-Key')
    if not api_key or len(api_key) == 0:
        return log_result(jsonify({"error":"unauthorized"}), 401)

    email = request.get_json().get('email')
    if not email:
        return log_result(jsonify({"error":"email parameter is missing"}), 400)

    for contact in contacts:
        if contact['email'] == email:
            return log_result(jsonify({"error":"duplicate"}), 422)

    latest_contact_id += 1
    contact = {
        "id": latest_contact_id,
        "email": email,
        "tags": []
    }
    contacts.append(contact)
    return log_result(jsonify(contact), 201)

# Add a POST method with the route /apo/contact/<contact_id>/tags, to assign a tag to a contact
@app.route('/api/contacts/<int:contact_id>/tags', methods=['POST'])
def assign_tag(contact_id):
    # log_request()

    # global contacts
    # global tags

    # api_key = request.headers.get('X-Api-Key')
    # if not api_key or len(api_key) == 0:
    #     return log_result(jsonify({"error":"unauthorized"}), 401)

    # tag_id = request.get_json().get('tag_id')
    # if not tag_id:
    #     return log_result(jsonify({"error":"tag_id parameter is missing"}), 400)

    # contact = next((contact for contact in contacts if contact['id'] == contact_id), None)
    # if not contact:
    #     return log_result(jsonify({"error":"contact not found"}), 404)

    # tag = next((tag for tag in tags if tag['id'] == tag_id), None)
    # if not tag:
    #     return log_result(jsonify({"error":"tag not found"}), 404)

    # contact['tags'].append(tag)
    # return log_result(jsonify(contact), 204)
    return log_result(jsonify({"error":"not implemented"}), 501)

@app.route('/api/contacts', methods=['GET'])
def list_contacts():
    log_request()

    email = request.args.get('email')

    global contacts
    if email:
        # Return a list containing only the matching contact
        selection = list(contact for contact in contacts if contact['email'] == email)
        return log_result(jsonify({'items': selection, 'hasMore': False}), 200)
    else:
        return log_result(jsonify({'items': contacts, 'hasMore': False}), 200)

def log_request():
    timestamp = str(time.time())
    with open('/var/log/requests.txt', 'a') as f:
        f.write('===================\n')
        f.write(timestamp + '\n\n')
        f.write(request.method + ' ' + request.url + '\n')
        f.write(str(request.headers))
        f.write(str(request.get_data(as_text=True)) + '\n')

def log_result(response, status_code):
    with open('/var/log/requests.txt', 'a') as f:
        f.write('-------------------\n')
        f.write(str(status_code) + '\n')
        f.write(str(response.json) + '\n')
    return response, status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
