import asyncio
import csv
import os
import pickle
import re

import aiohttp
import requests
from bs4 import BeautifulSoup


# Constants for the number of Devpost URLs to query and maximum concurrent connections
NUM_URLS_TO_QUERY = 10000
MAX_CONCURRENT_CONNECTIONS = 5


def get_current_path():
    """
    Get the current directory path where the script is located.

    Returns:
        str: The current directory path.
    """
    return os.path.dirname(os.path.abspath(__file__))


async def fetch_devpost_urls(session, page_num):
    """
    Asynchronously fetch Devpost project URLs for a given page number.

    Args:
        session (aiohttp.ClientSession): An aiohttp ClientSession for making asynchronous HTTP requests.
        page_num (int): The page number to fetch the Devpost URLs from.

    Returns:
        list: A list of Devpost project URLs for the given page number.
    """
    url = f'https://devpost.com/software/search?page={page_num}'
    await asyncio.sleep(5)

    try:
        async with session.get(url) as response:
            data = await response.json()
            projects = data.get('software')

        return [project['url'] for project in projects]
    except aiohttp.ContentTypeError as e:
        print(f"ContentTypeError: {e}")
        return []  # Return an empty list to signify that no URLs were fetched for this page.
    except Exception as e:
        print(f"Error fetching URLs for page {page_num}: {e}")
        return []  # Return an empty list for other exceptions as well.


async def fetch_all_devpost_urls():
    """
    Fetch Devpost URLs for all pages.

    Returns:
        list: A list of lists containing Devpost project URLs for each page.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_devpost_urls(session, page_num) for page_num in range(1, NUM_URLS_TO_QUERY + 1)]
        return await asyncio.gather(*tasks)


async def scrape_project_info(url):
    """
    Asynchronously scrape Devpost project information from a given URL.

    Args:
        url (str): The URL of the Devpost project page to scrape.

    Returns:
        tuple: A tuple containing a boolean indicating success of scraping, description, and technologies used.
    """
    await asyncio.sleep(5)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Extract project details parent component
        details_html = soup.find('body', id='body-softwares').find('section', id='container').\
            find('article', id='app-details').\
            find('div', id='app-details-left')

        # Get text containing description
        h2_tag = details_html.find('h2', string='What it does')
        content_under_h2 = []

        # Loop through the elements and check if they are h2 tags
        next_elements = h2_tag.find_next()
        while next_elements and next_elements.name != 'h2':
            content_under_h2.append(next_elements.get_text(strip=True))
            next_elements = next_elements.find_next()

        # Combine the plaintext content under "What it does" h2 header
        description = ' '.join(content_under_h2)

        # Navigate the HTML structure to find built-with element
        div_built_with = details_html.find('div', id='built-with')
        # Extract list of technologies
        technology_elements = div_built_with.find_all('a')
        technologies = [element.text.strip() for element in technology_elements]

        return True, description, technologies
    except AttributeError:
        # Handle the case when the elements cannot be found
        return False, '', []


async def update_csv_with_technologies(output_file):
    """
    Asynchronously update a CSV file with Devpost project information.

    Args:
        output_file (str): The path to the output CSV file.

    Returns:
        None
    """
    fieldnames = ['url', 'description', 'technologies']

    cache_file = os.path.join(get_current_path(), 'devpost_urls_cache.pkl')
    if os.path.exists(cache_file):
        url_list = read_cached_urls(cache_file)
    else:
        url_list = await fetch_all_devpost_urls()
        write_cached_urls(url_list=url_list, cache_file=cache_file)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        total_projects = 0
        successful_scrapes = 0
        failures = 0

        for urls in url_list:
            tasks = [scrape_project_info(url) for url in urls]
            results = await asyncio.gather(*tasks)

            for url, (is_scraped, description, technologies) in zip(urls, results):
                total_projects += 1
                description = re.sub(r'[^\w\s]', '', description).strip()

                # Check if all fields have data before writing the row
                if all([url, description, technologies]):
                    is_found_all_param = True
                    successful_scrapes += 1
                    row = {'url': url, 'description': description, 'technologies': ', '.join(technologies)}
                    await write_row(writer, row)
                else:
                    is_found_all_param = False
                    print(f'url: {url}\tdescription: {description}')
                    failures += 1

                print(f"Scraped project {total_projects}: Success={is_found_all_param}")

        print("\nScraping completed.")
        print(f"Total projects: {total_projects}")
        print(f"Successful scrapes: {successful_scrapes}")
        print(f"Failures: {failures}")


def read_cached_urls(cache_file):
    with open(cache_file, 'rb') as file:
        url_list = pickle.load(file)
        x = len(url_list[1])
        y = len(url_list)
        print(f'Used cache file with: {x*y} urls')
    return url_list


def write_cached_urls(cache_file, url_list):
    with open(cache_file, 'wb') as file:
        pickle.dump(url_list, file)
        x = len(url_list[1])
        y = len(url_list)
        print(f'Created cache file with: {x*y} urls')


async def write_row(writer, row):
    await asyncio.to_thread(writer.writerow, row)



if __name__ == '__main__':
    OUTPUT_CSV = 'devpost_scraper_output.csv'
    asyncio.run(update_csv_with_technologies(OUTPUT_CSV))
