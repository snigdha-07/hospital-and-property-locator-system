import requests
from bs4 import BeautifulSoup
import pandas as pd
from geopy.distance import geodesic
import os

def get_hospitals_in_hyderabad(output_file):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Overpass query for hospitals in Hyderabad
    overpass_query = """
    [out:xml];
    area[name="Hyderabad"]->.searchArea;
    node["amenity"="hospital"](area.searchArea);
    out body;
    """
    
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        print("Request successful, parsing XML...")
        soup = BeautifulSoup(response.content, 'xml')
        hospitals = []

        for node in soup.find_all('node'):
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            name_tag = node.find("tag", k="name")
            name = name_tag['v'] if name_tag else "Unnamed Hospital"
            hospitals.append({'name': name, 'latitude': lat, 'longitude': lon})

        df = pd.DataFrame(hospitals)

        if not df.empty:
            df.to_csv(output_file, index=False)
            print(f"All hospitals in Hyderabad saved to '{output_file}'.")
            return df  
        else:
            print("No hospital data found.")
            return pd.DataFrame()  
    else:
        print(f"Error {response.status_code}: Unable to fetch data from Overpass API")
        return pd.DataFrame()  

def get_area_coordinates(area_name):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Overpass query to get area coordinates
    overpass_query = f"""
    [out:json];
    node[name="{area_name}"];
    out center;
    """
    
    response = requests.get(overpass_url, params={'data': overpass_query})
    
    if response.status_code == 200:
        data = response.json()
        if 'elements' in data and len(data['elements']) > 0:
            lat = data['elements'][0]['lat']
            lon = data['elements'][0]['lon']
            return (lat, lon)
        else:
            print(f"No data found for the area '{area_name}'.")
            return None
    else:
        print(f"Error {response.status_code}: Unable to fetch data from Overpass API")
        return None

def filter_hospitals_within_radius(df, user_location, radius_km, output_file):
    filtered_hospitals = []

    for _, hospital in df.iterrows():
        hospital_location = (hospital['latitude'], hospital['longitude'])
        distance = geodesic(user_location, hospital_location).kilometers

        if distance <= radius_km:
            filtered_hospitals.append(hospital)

    filtered_df = pd.DataFrame(filtered_hospitals)

    if not filtered_df.empty:
        filtered_df.to_csv(output_file, index=False)
        print(f"Filtered hospitals within {radius_km} km saved to '{output_file}'.")
    else:
        print(f"No hospitals found within {radius_km} km of the specified location.")

if _name_ == "_main_":
    output_dir = "hospital_data"
    os.makedirs(output_dir, exist_ok=True)

    all_hospitals_file = os.path.join(output_dir, "hospitals_hyderabad.csv")
    
    hospitals_df = get_hospitals_in_hyderabad(all_hospitals_file)

    area_name = input("Enter the name of the area (e.g., Madhapur): ")
    
    user_location = get_area_coordinates(area_name)
    
    if user_location:
        radius_km = 3.0
        
        filtered_hospitals_file = os.path.join(output_dir, f"filtered_hospitals_within_{radius_km}km.csv")
        
        filter_hospitals_within_radius(hospitals_df, user_location, radius_km, filtered_hospitals_file)