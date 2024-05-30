import unittest
from unittest.mock import patch, Mock
import requests
from src.main import GitHub, Freshdesk

class TestGitHub(unittest.TestCase):
    def setUp(self):
        self.github = GitHub('token_abc')

    @patch('requests.get')
    def test_get_user_success(self, mock_get):
        mock_response = Mock()
        expected_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        result = self.github.get_user('johndoe')

        self.assertEqual(result['name'], expected_data['name'])
        self.assertEqual(result['email'], expected_data['email'])
        mock_get.assert_called_once_with('https://api.github.com/users/johndoe', headers={'Authorization': 'token token_abc'})

    @patch('requests.get')
    def test_get_user_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.github.get_user('nonexistent_user')

        self.assertEqual(str(context.exception), 'Invalid request')
        mock_get.assert_called_once_with('https://api.github.com/users/nonexistent_user', headers={'Authorization': 'token token_abc'})

class TestFreshdesk(unittest.TestCase):
    def setUp(self):
        self.freshdesk = Freshdesk('token_abc', 'subdomain_123', requests)

    @patch('requests.post')
    def test_create_contact_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 123, 'name': 'John Doe', 'email': 'john.doe@example.com'}
        mock_post.return_value = mock_response
        
        response = self.freshdesk.create_contact('John Doe', 'john.doe@example.com')
        
        self.assertEqual(response, {'id': 123, 'name': 'John Doe', 'email': 'john.doe@example.com'})
        mock_post.assert_called_once_with(
            'https://subdomain_123.freshdesk.com/api/v2/contacts',
            json={'name': 'John Doe', 'email': 'john.doe@example.com'},
            auth=self.freshdesk.auth
        )

    @patch('requests.post')
    def test_create_contact_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception):
            self.freshdesk.create_contact('John Doe', 'john.doe@example.com')
        
    @patch('requests.put')
    def test_update_contact_success(self, mock_put):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 123, 'name': 'John Updated', 'email': 'john.updated@example.com'}
        mock_put.return_value = mock_response
        
        response = self.freshdesk.update_contact(123, 'John Updated', 'john.updated@example.com')
        
        self.assertEqual(response, {'id': 123, 'name': 'John Updated', 'email': 'john.updated@example.com'})
        mock_put.assert_called_once_with(
            'https://subdomain_123.freshdesk.com/api/v2/contacts/123',
            json={'id': 123, 'name': 'John Updated', 'email': 'john.updated@example.com'},
            auth=self.freshdesk.auth
        )

    @patch('requests.get')
    def test_get_contact_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 123, 'name': 'John Doe', 'email': 'john.doe@example.com'}
        ]
        mock_get.return_value = mock_response
        
        response = self.freshdesk.get_contact('john.doe@example.com')
        
        self.assertEqual(response, {'id': 123, 'name': 'John Doe', 'email': 'john.doe@example.com'})
        mock_get.assert_called_once_with(
            'https://subdomain_123.freshdesk.com/api/v2/contacts',
            params={'email': 'john.doe@example.com'},
            auth=self.freshdesk.auth
        )

    @patch('requests.get')
    def test_get_contact_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        response = self.freshdesk.get_contact('nonexistent@example.com')
        
        self.assertIsNone(response)
        mock_get.assert_called_once_with(
            'https://subdomain_123.freshdesk.com/api/v2/contacts',
            params={'email': 'nonexistent@example.com'},
            auth=self.freshdesk.auth
        )

if __name__ == '__main__':
    unittest.main()
