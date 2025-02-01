import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import random
import time

# Initialize geolocator with Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")

# Function to geocode an address
def geocode_address(address):
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        time.sleep(1)
        return geocode_address(address)

# Function to generate nearby coordinates within 100 meters
def generate_nearby_coordinates(last_lat, last_long, max_offset=0.0009):
    lat_offset = random.uniform(-max_offset, max_offset)
    long_offset = random.uniform(-max_offset, max_offset)
    new_lat = last_lat + lat_offset if last_lat is not None else 17.3850  # Example default latitude
    new_long = last_long + long_offset if last_long is not None else 78.4867  # Example default longitude
    print(f"Generated nearby coordinates within 100m: ({new_lat}, {new_long})")
    return new_lat, new_long

# Read the Excel file
input_file = 'scraped_data after editing addresses.xlsx'  # Change to your file name
output_file = 'geocoded_addresses.xlsx'

# Load the addresses into a DataFrame
addresses_df = pd.read_excel(input_file)

# Ensure the DataFrame contains an 'Address' column
if 'Paragraphs' not in addresses_df.columns:
    raise ValueError("The input Excel file must contain a column named 'Paragraphs'.")

# Initialize Latitude and Longitude columns
addresses_df['Latitude'] = None
addresses_df['Longitude'] = None

# Track last known coordinates for fallback
last_known_lat, last_known_long = None, None

# Geocode each address
for index, row in addresses_df.iterrows():
    address = row['Paragraphs']
    lat, lon = geocode_address(address)

    # If geocoding fails, generate a nearby location within 100 meters
    if lat is None or lon is None:
        if last_known_lat is not None and last_known_long is not None:
            lat, lon = generate_nearby_coordinates(last_known_lat, last_known_long)
        else:
            lat, lon = generate_nearby_coordinates(17.3850, 78.4867)  # Default coordinates

    # Update last known coordinates if geocoding was successful
    if lat is not None and lon is not None:
        last_known_lat, last_known_long = lat, lon

    addresses_df.at[index, 'Latitude'] = lat
    addresses_df.at[index, 'Longitude'] = lon
    print(f'Geocoded: {address} -> Latitude: {lat}, Longitude: {lon}')

# Save the results to a new Excel file
addresses_df.to_excel(output_file, index=False)
print(f'Results saved to {output_file}')
