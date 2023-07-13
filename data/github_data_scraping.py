import requests
import csv
import base64
import string
import re

# Configurable constants
SECRET_GITHUB_TOKEN = ## Put github token here
NUM_PROJECTS_TO_SCRAPE = 1000
# feel free to adjust the query as you see fit (you cant have >5 conditionals but tried my best not fetch irrelevant projects)
query = 'stars:>1 license:mit NOT "interview questions" NOT "guide" NOT "tutorial" NOT "preparation" NOT "practice"'

# Other Contants
GITHUB_API_URL = 'https://api.github.com'
HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {SECRET_GITHUB_TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}

def get_repositories(page, per_page):
    url = f'{GITHUB_API_URL}/search/repositories'
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'page': page,
        'per_page': per_page,
        'repo': 'true'  # Include the repository information
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f'Repositories request failed with status code {response.status_code}')
        print(f'{response.content.decode("utf-8")}')
        return []

def get_readme(owner, repo):
    url = f'{GITHUB_API_URL}/repos/{owner}/{repo}/contents/README.md'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        response_json = response.json()
        if 'content' in response_json:
            content = response_json['content']
            readme = base64.b64decode(content).decode('utf-8')
            
            if readme:
                # Remove HTML tags
                cleaned_text = re.sub('<.*?>', '', readme)

                # Remove any links
                cleaned_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned_text)
                
                # Remove any markdown links
                cleaned_text = re.sub(r'\[.*?\]\(.*?\)', '', cleaned_text)

                # Extract the first sentence as the project description
                match = re.search(r'^(.*?[\.])', cleaned_text)
                if match:
                    cleaned_text = match.group(1)

                # Remove special characters and repeated characters
                #cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)

                # Collapse the readme to a single line
                cleaned_text = cleaned_text.replace('\n', ' ')
                
                cleaned_text = re.sub(r'(\s)\1+', r'\1', cleaned_text)

                return cleaned_text

            return readme
    return None

def get_languages(owner, repo):
    url = f'{GITHUB_API_URL}/repos/{owner}/{repo}/languages'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        languages = response.json()
        total_bytes = sum(languages.values())
        percentages = {lang: (count / total_bytes) * 100 for lang, count in languages.items()}
        return percentages
    else:
        print(f'Languages request failed with status code {response.status_code}')
        print(f'{response.content.decode("utf-8")}')
        return {}


def scrape_github_projects():
    total_projects = NUM_PROJECTS_TO_SCRAPE
    per_page = 100
    num_pages = (total_projects - 1) // per_page + 1

    data = []
    for page in range(1, num_pages + 1):
        print(f'Scraping page {page}/{num_pages}')
        repositories = get_repositories(page, per_page)
        for repository in repositories:
            owner = repository['owner']['login']
            repo = repository['name']
            readme = get_readme(owner, repo)
            languages = get_languages(owner, repo)  # New function to retrieve languages

            if readme:
                data.append([owner, repo, readme, languages])  # Include languages in the data

    return data

def save_to_csv(data):
    with open('github_readme.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Owner', 'Repository', 'Readme', 'Languages'])  # Include 'Languages' in the header row
        for item in data:
            owner, repo, readme, languages = item  # Unpack all four values
            readme = readme.replace('\n', ' ')
            writer.writerow([owner, repo, readme, languages])  # Include 'Languages' in the row
    print('Data saved to github_readme.csv')


if __name__ == '__main__':
    try:
        scraped_data = scrape_github_projects()
        save_to_csv(scraped_data)
    except Exception as e:
        print(f'An error occurred: {str(e)}')
