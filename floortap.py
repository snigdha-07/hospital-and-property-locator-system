import csv
from selenium import webdriver
from bs4 import BeautifulSoup
import time

def read_links_from_csv(input_file):
    with open(input_file, mode='r') as file:
        reader = csv.DictReader(file)
        return [row['Link'] for row in reader]  

def scrape_data_from_urls(links, base_url, p_class_name, h2_class_name, h6_class_name, output_file):
    driver = webdriver.Chrome()
    results = []

    try:
        for link in links:
            
            full_url = f"{base_url}{link}"
            driver.get(full_url)
            time.sleep(3)  

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            p_texts = [p.get_text(strip=True) for p in soup.find_all('p', class_=p_class_name)]
            h2_texts = [h2.get_text(strip=True) for h2 in soup.find_all('h2', class_=h2_class_name)]
                       
            h6_values = []
            for div in soup.find_all('div', class_=h6_class_name):
                h6_tags = div.find_all('h6')  
                for h6 in h6_tags:
                    h6_values.append(h6.get_text(strip=True))

            results.append({
                'URL': full_url,
                'Paragraphs': ' | '.join(p_texts),  
                'H2': ' | '.join(h2_texts),          
                'H6': ' | '.join(h6_values),          
            })

        print("Data scraping completed.")

        with open(output_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['URL', 'Paragraphs', 'H2', 'H6'])
            writer.writeheader()
            for data in results:
                writer.writerow(data)

        print(f'Successfully saved scraped data to {output_file}')

    finally:
        driver.quit()

input_links_file = 'scraped_links.csv'  
output_data_file = 'scraped_data.csv'  
base_url = 'https://www.floortap.com'  
p_class_name = 'miniWord'  
h2_class_name = 'buildingHead green'  
h6_class_name = 'col-6 col-sm-6 col-md-3 p-0 spaceDetailsInner'  

links = read_links_from_csv(input_links_file)

scrape_data_from_urls(links, base_url, p_class_name, h2_class_name, h6_class_name, output_data_file)
