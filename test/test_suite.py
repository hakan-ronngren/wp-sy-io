#!/usr/bin/env python3

import unittest
import requests

class TestAddSubscriber(unittest.TestCase):
    def test_add_subscriber_redirect(self):
        # Define the form parameters
        form_data = {
            'email': 'test@example.com',
            'redirect-to': 'https://example.com/success'
        }

        # Send the POST request to add-subscriber.php
        response = requests.post('http://php:8080/add-subscriber.php', data=form_data)

        # Assert that the response is a 303 See Other
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

if __name__ == '__main__':
    unittest.main()
