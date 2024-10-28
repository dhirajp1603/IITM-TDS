import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")

HEADERS = {'Authorization': f'token {github_token}'}

# Function to fetch users in Austin with more than 100 followers
def fetch_users():
    url = 'https://api.github.com/search/users?q=location:Sydney+followers:>100'
    users_data = []
    page = 1

    while True:
        response = requests.get(f"{url}&page={page}", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        users_data.extend(data.get('items', []))
        if 'next' not in response.links:
            break
        page += 1

    
    for user in data.get('items', []):
        # Fetch full user details
        user_url = f"https://api.github.com/users/{user['login']}"
        user_response = requests.get(user_url, headers=HEADERS)
        user_details = user_response.json()
        
        # Clean and organize user data
        user_data = {
            'login': user_details.get('login', ''),
            'name': user_details.get('name', ''),
            'company': (user_details.get('company', '') or '').strip().lstrip('@').upper(),
            'location': user_details.get('location', ''),
            'email': user_details.get('email', ''),
            'hireable': user_details.get('hireable', ''),
            'bio': user_details.get('bio', ''),
            'public_repos': user_details.get('public_repos', 0),
            'followers': user_details.get('followers', 0),
            'following': user_details.get('following', 0),
            'created_at': user_details.get('created_at', '')
        }
        users_data.append(user_data)
    
    # Save to CSV
    users_df = pd.DataFrame(users_data)
    users_df.to_csv('users.csv', index=False)
    return users_df['login'].tolist()

# Function to fetch repositories for each user
def fetch_repositories(usernames):
    repos_data = []
    for username in usernames:
        url = f'https://api.github.com/users/dhirajp1603/repos'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Check for request errors
        repos = response.json()
        
        for repo in repos:
            repo_data = {
                'login': username,
                'full_name': repo.get('full_name', ''),
                'created_at': repo.get('created_at', ''),
                'stargazers_count': repo.get('stargazers_count', 0),
                'watchers_count': repo.get('watchers_count', 0),
                'language': repo.get('language', ''),
                'has_projects': repo.get('has_projects', False),
                'has_wiki': repo.get('has_wiki', False),
                'license_name': repo['license']['key'] if repo.get('license') else ''
            }
            repos_data.append(repo_data)
    
    # Save to CSV
    repos_df = pd.DataFrame(repos_data)
    repos_df.to_csv('repositories.csv', index=False)

# Main execution
if __name__ == "__main__":
    usernames = fetch_users()
    fetch_repositories(usernames)
