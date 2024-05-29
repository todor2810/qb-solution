import os
from typing import TypedDict
import click
import requests

class GitHubUser(TypedDict):
    name: str
    email: str

class FreshdeskContact(TypedDict):
    id: int
    name: str
    email: str

class GitHub:
    domain = 'https://api.github.com'

    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

    def get_user(self, username) -> GitHubUser:
        url = f"{self.domain}/users/{username}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception('Invalid request')

        return {
            'name': response.json()['name'],
            'email': response.json()['email']
        }

class Freshdesk:
    def __init__(self, token, subdomain, requests):
        self.domain = f'https://{subdomain}.freshdesk.com'
        self.auth = requests.auth.HTTPBasicAuth(token, "X")
        self.requests = requests

    def create_contact(self, name, email):
        url = f'{self.domain}/api/v2/contacts'
        data = {'name': name, 'email': email}
        response = requests.post(url, json=data, auth=self.auth)

        if response.status_code != 200:
            raise Exception('Invalid request')
        
        return response.json()

    def update_contact(self, id, name, email):
        url = f'{self.domain}/api/v2/contacts/{id}'
        data = {'id': id, 'name': name, 'email': email}
        response = requests.put(url, json=data, auth=self.auth)

        if response.status_code != 200:
            raise Exception('Invalid request')
        
        return response.json()

    def get_contact(self, email) -> FreshdeskContact:
        url = f'{self.domain}/api/v2/contacts'
        params = {'email': email}
        response = self.requests.get(url, params=params, auth=self.auth)

        if response.status_code != 200:
            raise Exception('Invalid request')
        
        contacts = response.json()

        if not contacts:
            return None
        
        contact = contacts[0]
        return {
            'id': contact['id'],
            'name': contact['name'],
            'email': contact['email']
        }

@click.command()
@click.argument('gh_username')
@click.argument('fd_subdomain')
def main(gh_username, fd_subdomain):
    gh_token = os.getenv('GITHUB_TOKEN')
    fd_token = os.getenv('FRESHDESK_TOKEN')

    if not gh_token:
        raise Exception('Missing $GITHUB_TOKEN')
    
    if not fd_token:
        raise Exception('Missing $FRESHDESK_TOKEN')

    github = GitHub(gh_token)
    freshdesk = Freshdesk(fd_token, fd_subdomain, requests)

    gh_user = github.get_user(gh_username)
    fd_contact = freshdesk.get_contact(gh_user['email'])

    if not fd_contact:
        freshdesk.create_contact(**gh_user)
        print('Successfully created contact.')
    else:
        freshdesk.update_contact(**fd_contact)
        print('Successfully updated contact.')

if __name__ == '__main__':
    main()
