#!/usr/bin/env python3

from flask import Flask, request, jsonify

import time

app = Flask(__name__)

#-------------------
# Test Endpoints

contacts = []
latest_contact_id = 0
is_broken = False

tags = [
    {'id': 1, 'name': 'tag1'},
    {'id': 2, 'name': 'tag2'},
    {'id': 3, 'name': 'tag3'}
]

slack_payloads = []

# Only used as a readiness probe
@app.route('/')
def root():
    log_request()

    return log_result(jsonify({'result': 'OK'}), 200)

@app.route('/test/reset', methods=['POST'])
def reset():
    log_request()

    global is_broken
    is_broken = False

    global contacts
    contacts = []

    global latest_contact_id
    latest_contact_id = 0

    global slack_payloads
    slack_payloads = []

    return log_result(jsonify({'result': 'OK'}), 204)

@app.route('/test/break', methods=['POST'])
def break_server():
    log_request()

    global is_broken
    is_broken = True
    return log_result(jsonify({'result': 'OK'}), 204)

@app.route('/test/slack/payloads', methods=['GET'])
def get_slack_payloads():
    log_request()
    return log_result(jsonify(slack_payloads), 200)

#-------------------
# Systeme.IO Endpoints

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    log_request()

    global is_broken
    if is_broken:
        return log_result(jsonify({"error":"emulating broken backend"}), 500)

    global latest_contact_id
    global contacts

    api_key = request.headers.get('X-API-Key')
    if not api_key or len(api_key) == 0:
        return log_result(jsonify({"error":"unauthorized"}), 401)

    new_contact = request.get_json()

    email = new_contact.get('email')
    if not email:
        return log_result(jsonify({"error":"email parameter is missing"}), 400)

    for contact in contacts:
        if contact['email'] == email:
            return log_result(jsonify({"error":"duplicate"}), 422)

    # If the contact has fields, verify that fields is a list of dictionaries, each of which has 'slug' and 'value' keys
    fields = new_contact.get('fields')
    if fields:
        if not isinstance(fields, list):
            return log_result(jsonify({"error":"fields must be a list"}), 400)
        for field in fields:
            if not isinstance(field, dict):
                return log_result(jsonify({"error":"each field must be a dictionary"}), 400)
            if 'slug' not in field or 'value' not in field:
                return log_result(jsonify({"error":"each field must have 'slug' and 'value' keys"}), 400)

    latest_contact_id += 1
    contact = {
        "id": latest_contact_id,
        "email": email,
        "tags": [],
        "fields": new_contact.get('fields', [])
    }
    contacts.append(contact)
    return log_result(jsonify(contact), 201)

@app.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
def update_contact(contact_id):
    log_request()

    global is_broken
    if is_broken:
        return log_result(jsonify({"error":"emulating broken backend"}), 500)

    global contacts

    api_key = request.headers.get('X-API-Key')
    if not api_key or len(api_key) == 0:
        return log_result(jsonify({"error":"unauthorized"}), 401)

    contact = next((contact for contact in contacts if contact['id'] == contact_id), None)
    if not contact:
        return log_result(jsonify({"error":"contact not found"}), 404)

    # Verify content-type = application/merge-patch+json
    if request.headers.get('Content-Type') != 'application/merge-patch+json':
        return log_result(jsonify({"error":"Content-Type must be application/merge-patch+json"}), 415)

    new_contact_data = request.get_json()

    if 'email' in new_contact_data:
        contact['email'] = new_contact_data['email']

    if 'fields' in new_contact_data:
        fields = new_contact_data['fields']
        for field in fields:
            field_slug = field['slug']
            field_value = field['value']
            existing_field = next((f for f in contact['fields'] if f['slug'] == field_slug), None)
            if existing_field:
                existing_field['value'] = field_value
            else:
                contact['fields'].append({'slug': field_slug, 'value': field_value})

    return log_result(jsonify(contact), 200)

@app.route('/api/contacts/<int:contact_id>/tags', methods=['POST'])
def assign_tag(contact_id):
    log_request()

    global is_broken
    if is_broken:
        return log_result(jsonify({"error":"emulating broken backend"}), 500)

    global contacts
    global tags

    api_key = request.headers.get('X-API-Key')
    if not api_key or len(api_key) == 0:
        return log_result(jsonify({"error":"unauthorized"}), 401)

    tag_id = request.get_json().get('tagId')
    if not tag_id:
        return log_result(jsonify({"error":"tagId parameter is missing"}), 400)

    contact = next((contact for contact in contacts if contact['id'] == contact_id), None)
    if not contact:
        return log_result(jsonify({"error":"contact not found"}), 404)

    # If the contact already has the tag, act as if the tag was successfully assigned
    if next((tag for tag in contact['tags'] if tag['id'] == tag_id), None):
        return log_result(jsonify(contact), 204)

    # Look up the tag by ID and assign it to the contact
    tag = next((tag for tag in tags if tag['id'] == tag_id), None)
    if not tag:
        return log_result(jsonify({"error":"tag not found"}), 404)
    contact['tags'].append(tag)
    return log_result(jsonify(contact), 204)

@app.route('/api/contacts', methods=['GET'])
def list_contacts():
    log_request()

    global is_broken
    if is_broken:
        return log_result(jsonify({"error":"emulating broken backend"}), 500)

    email = request.args.get('email')

    global contacts
    if email:
        # Return a list containing only the matching contact
        selection = list(contact for contact in contacts if contact['email'] == email)
        return log_result(jsonify({'items': selection, 'hasMore': False}), 200)
    else:
        return log_result(jsonify({'items': contacts, 'hasMore': False}), 200)

@app.route('/api/tags', methods=['GET'])
def list_tags():
    log_request()

    global is_broken
    if is_broken:
        return log_result(jsonify({"error":"emulating broken backend"}), 500)

    query = request.args.get('query')

    global tags
    if query:
        # Return a list containing only the matching tags
        selection = list(tag for tag in tags if tag['name'] == query)
        return log_result(jsonify({'items': selection, 'hasMore': False}), 200)
    else:
        return log_result(jsonify({'items': tags, 'hasMore': False}), 200)

#-------------------
# Slack Endpoints

@app.route('/api/chat.postMessage', methods=['POST'])
def post_message():
    log_request()

    authorization = request.headers.get('Authorization')
    if not authorization or authorization != 'Bearer 123':
        return log_result(jsonify({"error":"unauthorized"}), 401)

    global slack_payloads
    slack_payloads.append(request.get_json())

    return log_result(jsonify({'result': 'OK'}), 200)

#-------------------
# Helper Functions

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
