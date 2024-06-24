#!/usr/bin/env python3

import unittest
import requests

class TestAddSubscriber(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

    def test_add_new_subscriber(self):
        form_data = {
            'email': 'test@example.com',
            'redirect-to': 'https://example.com/success'
        }

        response = requests.post('http://web:8080/add-subscriber.php', data=form_data, allow_redirects=False)

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        self.assert_subscriber_exists(form_data['email'])

    def test_add_new_subscriber_missing_email(self):
        form_data = {
            'redirect-to': 'https://example.com/success'
        }

        response = requests.post('http://web:8080/add-subscriber.php', data=form_data, allow_redirects=False)

        self.assertEqual(response.status_code, 400)

    def test_add_new_subscriber_missing_redirect_to(self):
        form_data = {
            'email': 'test@example.com'
        }

        response = requests.post('http://web:8080/add-subscriber.php', data=form_data, allow_redirects=False)

        self.assertEqual(response.status_code, 400)

    def test_add_subscriber_and_assign_tag(self):
        # Add a new subscriber
        form_data = {
            'email': 'test@example.com',
            'redirect-to': 'https://example.com/success',
            'tags': 'tag1'
        }

        response = requests.post('http://web:8080/add-subscriber.php', data=form_data, allow_redirects=False)

        self.assertEqual(response.status_code, 303)

        self.assert_subscriber_has_tags(form_data['email'], ['tag1'])

    # TODO: test that a new tag is set when the user is already subscribed
    # TODO: test that the tag is still there when a tag is set and the user is already subscribed with a tag
    # TODO: test that multiple tags can be set
    # TODO: test that an additional tag can be set when the user is already subscribed with a tag
    # TODO: test that the tags are still there when multiple tags are set and the user is already subscribe with one of the tags
    # TODO: test that a tag can be both created and assigned to a user

    # --- Utility Functions ---

    def assert_subscriber_exists(self, email):
        response = requests.get('http://localhost:8081/api/contacts?email=' + email, headers={"X-Api-Key":"123"})
        contact = response.json()['items'][0]
        self.assertEqual(contact['email'], email)

    def assert_subscriber_has_tags(self, email, tags):
        response = requests.get('http://localhost:8081/api/contacts?email=' + email, headers={"X-Api-Key":"123"})
        contact = response.json()['items'][0]
        self.assertEqual(contact['email'], email)
        self.assertEqual(set(tag['name'] for tag in contact['tags']), set(tags))

if __name__ == '__main__':
    unittest.main()
