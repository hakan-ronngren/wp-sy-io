#!/usr/bin/env python3

import unittest
import requests

TEST_EMAIL = 'test@example.com'
SUCCESS_URL = 'https://example.com/success'

class TestPostAddContactPHP(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

    def test_add_new_contact_without_name(self):
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assertEqual(contact['fields'], [])

    def test_add_new_contact_with_name(self):
        form_data = {
            'first_name': 'John',
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assertEqual(contact.get('fields'), [{'slug': 'first_name', 'value': form_data['first_name']}])

    def test_add_contact_with_spaces_before_and_after_parameters(self):
        # Relevant parameters are the ones that the user can fill in the form
        form_data = {
            'first_name': ' John ',
            'email': ' ' + TEST_EMAIL + ' ',
            'redirect-to': SUCCESS_URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(TEST_EMAIL)
        self.assertEqual(contact.get('fields'), [{'slug': 'first_name', 'value': 'John'}])


    def test_add_contact_with_a_northern_european_name(self):
        form_data = {
            'first_name': 'Håkan',
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL
        }
        response = requests.post(
            'http://web:8080/add-systeme-io-contact.php',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assertEqual(contact.get('fields'), [{'slug': 'first_name', 'value': form_data['first_name']}])

    def test_add_contact_with_a_japanese_name(self):
        form_data = {
            'first_name': '千代子',
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL
        }
        response = requests.post(
            'http://web:8080/add-systeme-io-contact.php',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assertEqual(contact.get('fields'), [{'slug': 'first_name', 'value': form_data['first_name']}])

    def test_add_new_contact_invalid_name(self):
        form_data = {
            'first_name': 'John\'--', # Probable SQL injection attempt
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 400)

    def test_add_new_contact_missing_email(self):
        form_data = {
            'first_name': 'John',
            'redirect-to': SUCCESS_URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 400)

    def test_add_new_contact_invalid_email(self):
        form_data = {
            'first_name': 'John',
            'email': 'test', # Invalid email
            'redirect-to': SUCCESS_URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 400)

    def test_add_new_contact_missing_redirect_to(self):
        form_data = {
            'first_name': 'John',
            'email': TEST_EMAIL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 400)

    def test_add_new_contact_invalid_redirect_to(self):
        form_data = {
            'first_name': 'John',
            'email': TEST_EMAIL,
            'redirect-to': 'invalid-url' # Invalid URL
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 400)

    def test_add_contact_and_assign_tag(self):
        # Add a new contact
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL,
            'tags': 'tag1'
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assert_contact_has_tags(contact, ['tag1'])

    def test_add_contact_and_assign_multiple_tags(self):
        # Add a new contact
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL,
            'tags': 'tag1,tag2'
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assert_contact_has_tags(contact, ['tag1', 'tag2'])

    def test_add_contact_and_assign_existing_tag(self):
        # Add a new contact
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL,
            'tags': 'tag1'
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        # Subscribe again, with the same tag
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assert_contact_has_tags(contact, ['tag1'])

    def test_add_contact_and_assign_additional_tag(self):
        # Add a new contact
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL,
            'tags': 'tag1'
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        # Subscribe again, with a different tag
        form_data['tags'] = 'tag2'
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])
        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assert_contact_has_tags(contact, ['tag1', 'tag2'])

    def test_set_first_name_after_adding_contact_without_name(self):
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL,
            'first_name': ''
        }

        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        # Update the contact's first name
        form_data['first_name'] = 'John'
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assertEqual(contact.get('fields'), [{'slug': 'first_name', 'value': form_data['first_name']}])

    def test_change_first_name(self):
        # Add a new contact
        form_data = {
            'email': TEST_EMAIL,
            'redirect-to': SUCCESS_URL,
            'first_name': 'John'
        }
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        # Update the contact's first name
        form_data['first_name'] = 'Jane'
        response = requests.post('http://web:8080/add-systeme-io-contact.php', data=form_data, allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], form_data['redirect-to'])

        contact = self.assert_get_contact_succeeds(form_data['email'])
        self.assertEqual(contact.get('fields'), [{'slug': 'first_name', 'value': form_data['first_name']}])

    # TODO: Test that a 500 from the API results in a redirect to the error page (new functionality)

    # --- Utility Functions ---

    def assert_get_contact_succeeds(self, email):
        response = requests.get('http://localhost:8081/api/contacts?email=' + email, headers={"X-API-Key":"123"})
        contact = response.json()['items'][0]
        self.assertEqual(contact['email'], email)
        return contact

    def assert_contact_has_tags(self, contact, tags):
        self.assertEqual(len(contact['tags']), len(tags))
        for tag in list(tag['name'] for tag in contact['tags']):
            self.assertIn(tag, tags)

if __name__ == '__main__':
    unittest.main()
