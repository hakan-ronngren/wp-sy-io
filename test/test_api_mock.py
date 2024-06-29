import unittest
import requests

# Test the API mock so we can use it to test the web application

TEST_EMAIL = 'test@example.com'

class TestCreateContact(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

    def test_create_contact(self):
        contact_data = {
            'email': TEST_EMAIL
        }
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 201)
        contact = response.json()

        # Verify the contact details
        self.assertEqual(contact['email'], TEST_EMAIL)
        self.assertEqual(contact['tags'], [])
        self.assertEqual(contact['fields'], [])

    def test_create_contact_duplicate(self):
        contact_data = {
            'email': TEST_EMAIL
        }
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 201)

        # Subscribe the same contact again
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 422)

    def test_create_contact_missing_email(self):
        contact_data = {}
        response = requests.post('http://localhost:8081/api/contacts', json=contact_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 400)

    def test_create_contact_with_first_name(self):
        requests.post('http://localhost:8081/test/reset')

        self.contact_data = {
            'email': TEST_EMAIL,
            'fields': [
                {'slug': 'first_name', 'value': 'John'}
            ]
        }
        response = requests.post('http://localhost:8081/api/contacts', json=self.contact_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 201)
        contact = response.json()

        # Verify the contact details
        self.assertEqual(len(contact['fields']), 1)
        field = contact['fields'][0]
        self.assertEqual(field['slug'], 'first_name')
        self.assertEqual(field['value'], 'John')


class TestUpdateContact(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

        # Add a new contact
        self.contact_data = {
            'email': TEST_EMAIL,
            'fields': [
                {'slug': 'first_name', 'value': 'John'},
                {'slug': 'last_name', 'value': 'Doe'}
            ]
        }
        requests.post('http://localhost:8081/api/contacts', json=self.contact_data, headers={'X-API-Key': '123'})

    def test_change_email(self):
        new_contact_data = {
            'email': 'test2@example.com'
        }
        response = requests.patch('http://localhost:8081/api/contacts/1', json=new_contact_data, headers={'X-API-Key': '123', 'Content-Type': 'application/merge-patch+json'})
        self.assertEqual(response.status_code, 200)

        # Verify the contact details
        response = requests.get(f'http://localhost:8081/api/contacts', headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contacts = response.json()
        self.assertEqual(len(contacts['items']), 1)
        contact = contacts['items'][0]
        self.assertEqual(contact['email'], new_contact_data['email'])
        self.assertEqual(len(contact['fields']), 2)

    def test_change_first_name(self):
        new_contact_data = {
            'fields': [
                {'slug': 'first_name', 'value': 'Jane'}
            ]
        }
        response = requests.patch('http://localhost:8081/api/contacts/1', json=new_contact_data, headers={'X-API-Key': '123', 'Content-Type': 'application/merge-patch+json'})
        self.assertEqual(response.status_code, 200)

        # Verify the contact details
        response = requests.get(f'http://localhost:8081/api/contacts', headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contacts = response.json()
        self.assertEqual(len(contacts['items']), 1)
        contact = contacts['items'][0]
        self.assertEqual(len(contact['fields']), 2)
        for field in contact['fields']:
            if field['slug'] == 'first_name':
                self.assertEqual(field['value'], new_contact_data['fields'][0]['value'])
            elif field['slug'] == 'last_name':
                self.assertEqual(field['value'], self.contact_data['fields'][1]['value'])
            else:
                self.fail('Unexpected field in response: ' + str(field))

class TestAssignTag(unittest.TestCase):
    def setUp(self):
        requests.post('http://localhost:8081/test/reset')

        # Add a new contact
        self.contact_data = {
            'email': TEST_EMAIL
        }
        response = requests.post('http://localhost:8081/api/contacts', json=self.contact_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 201)
        self.contact = response.json()

    def test_assign_tag(self):
        contact_data = self.contact_data
        contact = self.contact

        # Assign a tag to the contact
        tag_data = {
            'tagId': 1
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Verify that the tag is assigned to the contact
        response = requests.get(f'http://localhost:8081/api/contacts?email={contact_data["email"]}', headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contact = response.json()
        self.assertEqual(len(contact['items']), 1)
        self.assertEqual(len(contact['items'][0]['tags']), 1)
        self.assertEqual(contact['items'][0]['tags'][0]['id'], 1)

    def test_assign_tag_missing_tag_id(self):
        contact = self.contact

        # Assign a tag to the contact without a tag ID
        tag_data = {}
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 400)

    def test_assign_tag_missing_contact(self):
        # Assign a tag to a contact that does not exist
        tag_data = {
            'tagId': 1
        }
        response = requests.post('http://localhost:8081/api/contacts/2/tags', json=tag_data, headers={'X-API-Key': '123'})
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
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 204)

        tag_data = {
            'tagId': 2
        }
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Verify that the tags are assigned to the contact
        response = requests.get(f'http://localhost:8081/api/contacts?email={contact_data["email"]}', headers={'X-API-Key': '123'})
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
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Assign the same tag to the contact again
        response = requests.post(f'http://localhost:8081/api/contacts/{contact["id"]}/tags', json=tag_data, headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 204)

        # Verify that the tag is assigned to the contact only once
        response = requests.get(f'http://localhost:8081/api/contacts?email={contact_data["email"]}', headers={'X-API-Key': '123'})
        self.assertEqual(response.status_code, 200)
        contact = response.json()
        self.assertEqual(len(contact['items']), 1)
        self.assertEqual(len(contact['items'][0]['tags']), 1)
        self.assertEqual(contact['items'][0]['tags'][0]['id'], 1)


if __name__ == '__main__':
    unittest.main()
