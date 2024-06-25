import unittest
import requests

# Test the API mock so we can use it to test the web application

class TestSubscribe(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

    def test_subscribe(self):
        # Subscribe a new contact
        contact_data = {
            'email': 'test@example.com'
        }
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 201)
        contact = response.json()

        # Verify the contact details
        self.assertEqual(contact['email'], 'test@example.com')
        self.assertEqual(contact['tags'], [])

    def test_subscribe_duplicate(self):
        # Subscribe a new contact
        contact_data = {
            'email': 'test@example.com'
        }
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 201)

        # Subscribe the same contact again
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 422)

    def test_subscribe_missing_email(self):
        # Subscribe a new contact without an email
        contact_data = {}
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 400)

class TestAssignTag(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

        # Add a new contact
        self.contact_data = {
            'email': 'test@example.com'
        }
        response = requests.post('http://localhost:8081/api/contacts', json=self.contact_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 201)
        self.contact = response.json()

    def test_assign_tag(self):
        contact_data = self.contact_data
        contact = self.contact

        # Assign a tag to the contact
        tag_data = {
            'tagId': 1
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Verify that the tag is assigned to the contact
        response = requests.get(f'http://localhost:8081/api/contacts?email={contact_data["email"]}', headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contact = response.json()
        self.assertEqual(len(contact['items']), 1)
        self.assertEqual(len(contact['items'][0]['tags']), 1)
        self.assertEqual(contact['items'][0]['tags'][0]['id'], 1)

    def test_assign_tag_missing_tag_id(self):
        contact = self.contact

        # Assign a tag to the contact without a tag ID
        tag_data = {}
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 400)

    def test_assign_tag_missing_contact(self):
        # Assign a tag to a contact that does not exist
        tag_data = {
            'tagId': 1
        }
        response = requests.post('http://localhost:8081/api/contacts/2/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 404)

    def test_assign_tag_unauthorized(self):
        contact = self.contact

        # Assign a tag to a contact without an API key
        tag_data = {
            'tagId': 1
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data)
        self.assertEqual(response.status_code, 401)

    def test_assign_two_tags(self):
        contact_data = self.contact_data
        contact = self.contact

        # Assign two tags to the contact
        tag_data = {
            'tagId': 1
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 204)

        tag_data = {
            'tagId': 2
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Verify that the tags are assigned to the contact
        response = requests.get(f'http://localhost:8081/api/contacts?email={contact_data["email"]}', headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contact = response.json()
        self.assertEqual(len(contact['items']), 1)
        self.assertEqual(len(contact['items'][0]['tags']), 2)
        self.assertEqual(contact['items'][0]['tags'][0]['id'], 1)
        self.assertEqual(contact['items'][0]['tags'][1]['id'], 2)

    def test_assign_tag_duplicate(self):
        contact_data = self.contact_data
        contact = self.contact

        # Assign a tag to the contact
        tag_data = {
            'tagId': 1
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Assign the same tag to the contact again
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Verify that the tag is assigned to the contact only once
        response = requests.get(f'http://localhost:8081/api/contacts?email={contact_data["email"]}', headers={'X-Api-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contact = response.json()
        self.assertEqual(len(contact['items']), 1)
        self.assertEqual(len(contact['items'][0]['tags']), 1)
        self.assertEqual(contact['items'][0]['tags'][0]['id'], 1)


if __name__ == '__main__':
    unittest.main()
