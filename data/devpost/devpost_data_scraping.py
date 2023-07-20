import csv
import requests
from bs4 import BeautifulSoup
import os

def scrape_project_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Navigate the HTML structure to find the desired elements
        div_built_with = soup.find('body', id='body-softwares').find('section', id='container').\
            find('article', id='app-details').\
            find('div', id='app-details-left').\
            find('div', id='built-with')

        # Extract project description
        description = div_built_with.find_previous('div').text.strip()

        # Extract list of technologies
        technology_elements = div_built_with.find_all('a')
        technologies = [element.text.strip() for element in technology_elements]

        return True, description, technologies
    except AttributeError:
        # Handle the case when the elements cannot be found
        return False, '', []

def update_csv_with_technologies(input_file, output_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_file)
    output_path = os.path.join(script_dir, output_file)

    with open(input_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['technologies']

        with open(output_path, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            total_projects = 0
            successful_scrapes = 0
            failures = 0

            for row in reader:
                project_url = row['url']
                total_projects += 1

                success, description, technologies = scrape_project_info(project_url)

                if success:
                    successful_scrapes += 1
                    row['technologies'] = ', '.join(technologies)
                else:
                    failures += 1

                writer.writerow(row)

                print(f"Scraped project {total_projects}: Success={success}")

            print(f"\nScraping completed.")
            print(f"Total projects: {total_projects}")
            print(f"Successful scrapes: {successful_scrapes}")
            print(f"Failures: {failures}")

if __name__ == '__main__':
    input_csv = 'input_data.csv'
    output_csv = 'projects_with_technologies.csv'

    update_csv_with_technologies(input_csv, output_csv)
