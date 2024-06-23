#!/usr/bin/env python3

import unittest
import requests

class TestAddSubscriber(unittest.TestCase):
    def test_add_new_subscriber(self):
        form_data = {
            'email': 'test@example.com',
            'redirect-to': 'https://example.com/success'
        }

        response = requests.post('http://web:8080/add-subscriber.php', data=form_data, allow_redirects=False)

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

if __name__ == '__main__':
    unittest.main()
