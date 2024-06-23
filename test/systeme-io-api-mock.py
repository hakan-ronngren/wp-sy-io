#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def root():
    return 'OK'

# Accept a POST request with a parameter "email"
@app.route('/api/contacts', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    return jsonify({
        "id": 265433598,
        "email": email,
        "registeredAt": "2024-06-23T06:44:54+00:00",
        "locale": "en",
        "sourceURL": None,
        "unsubscribed": False,
        "bounced": False,
        "needsConfirmation": False,
        "fields": [],
        "tags": []
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
