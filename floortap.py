import csv
from selenium import webdriver
from bs4 import BeautifulSoup
import time

# Function to read incomplete links from a CSV file
def read_links_from_csv(input_file):
    with open(input_file, mode='r') as file:
        reader = csv.DictReader(file)
        return [row['Link'] for row in reader]  # Assumes the header is 'Link'

# Function to scrape data from generated URLs
def scrape_data_from_urls(links, base_url, p_class_name, h2_class_name, h6_class_name, output_file):
    driver = webdriver.Chrome()
    results = []

    try:
        for link in links:
            # Complete the URL
            full_url = f"{base_url}{link}"
            driver.get(full_url)
            time.sleep(3)  # Wait for the page to load

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract required data
            p_texts = [p.get_text(strip=True) for p in soup.find_all('p', class_=p_class_name)]
            h2_texts = [h2.get_text(strip=True) for h2 in soup.find_all('h2', class_=h2_class_name)]
            
            # Extracting <h6> values correctly
            h6_values = []
            for div in soup.find_all('div', class_=h6_class_name):
                h6_tags = div.find_all('h6')  # Now find all <h6> tags within each <div>
                for h6 in h6_tags:
                    h6_values.append(h6.get_text(strip=True))

            results.append({
                'URL': full_url,
                'Paragraphs': ' | '.join(p_texts),  # Join paragraphs with a separator
                'H2': ' | '.join(h2_texts),          # Join H2 texts with a separator
                'H6': ' | '.join(h6_values),          # Join H6 values with a separator
            })

        print("Data scraping completed.")

        # Save scraped data to a CSV file
        with open(output_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['URL', 'Paragraphs', 'H2', 'H6'])
            writer.writeheader()
            for data in results:
                writer.writerow(data)

        print(f'Successfully saved scraped data to {output_file}')

    finally:
        driver.quit()

# Usage
input_links_file = 'scraped_links.csv'  # CSV file containing incomplete hrefs
output_data_file = 'scraped_data.csv'  # Output CSV file for scraped data
base_url = 'https://www.floortap.com'  # Base URL for completing hrefs
p_class_name = 'miniWord'  # Class name for <p>
h2_class_name = 'buildingHead green'  # Class name for <h2>
h6_class_name = 'col-6 col-sm-6 col-md-3 p-0 spaceDetailsInner'  # Class name for div containing <h6>

# Step 1: Read incomplete links from CSV
links = read_links_from_csv(input_links_file)

# Step 2: Scrape data from the generated URLs
scrape_data_from_urls(links, base_url, p_class_name, h2_class_name, h6_class_name, output_data_file)
