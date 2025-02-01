import pandas as pd
import streamlit as st
import folium
from geopy.distance import geodesic
from streamlit_folium import folium_static

# Load the Excel data
data_path = r'C:\Users\BHEL\Desktop\complete excel.xlsx'
df = pd.read_excel(data_path)


# Initialize session state to keep track of selected area and specialty
if 'area_selected' not in st.session_state:
    st.session_state.area_selected = None
if 'specialty_selected' not in st.session_state:
    st.session_state.specialty_selected = None

# Function to calculate population index based on an algorithm from PDF
def calculate_population_index(data):
    # Example: Calculate population index based on population density, hospital count, and other factors
    data['Population Index'] = data['Population_Density'] / (1 + data['hospital_count'])
    return data

# Function to filter by area, specialty, and population index
def filter_by_criteria(data, area, specialty, min_population_index=500):  # Adjust threshold as needed
    # Apply area, specialty, and population index filtering
    filtered_data = data[(data['Area'] == area) & 
                         (data['Speciality'] == specialty) &
                         (data['Population Index'] >= min_population_index)]
    return filtered_data

# Function to filter hospitals by distance <= 5 km
def filter_hospitals_by_distance(df, area_coords):
    filtered_hospitals = []
    for _, row in df.iterrows():
        hospital_coords = (row['latitude'], row['longitude'])
        distance = geodesic(area_coords, hospital_coords).km
        if distance <= 5:
            filtered_hospitals.append(row)
    return pd.DataFrame(filtered_hospitals)

# Page Navigation
page = st.sidebar.radio("Navigation", ["Menu", "Map"])

if page == "Menu":
    st.title("Hospital Locator Menu")

    # Area and Specialty Selection
    area_options = df['PD-Area'].unique()
    specialty_options = df['Speciality'].unique()

    selected_area = st.selectbox("Select Area", area_options)
    selected_specialty = st.selectbox("Select Hospital Specialty", specialty_options)

    # Submit Button
    if st.button("Submit"):
        st.session_state.area_selected = selected_area
        st.session_state.specialty_selected = selected_specialty
        st.experimental_rerun()  # Refreshes the app to trigger the Map page

elif page == "Map":
    # Check if area and specialty are selected
    if not (st.session_state.area_selected and st.session_state.specialty_selected):
        st.write("Please go to the Menu page to select an area and specialty.")
    else:
        # Display the map based on selected area and specialty
        st.title("Nearby Hospitals and Properties")

        selected_area = st.session_state.area_selected
        selected_specialty = st.session_state.specialty_selected

        # Calculate population index before filtering
        df = calculate_population_index(df)

        # Get lat/long for the selected area
        area_data = df[df['Area'] == selected_area].iloc[0]
        area_coords = (area_data['Latitude'], area_data['Longitude'])

        # Filter hospitals based on area, specialty, and population index
        filtered_df = filter_by_criteria(df, selected_area, selected_specialty)
        # Further filter hospitals by distance within 5 km radius
        nearby_hospitals = filter_hospitals_by_distance(filtered_df, area_coords)

        # Create map centered on the selected area
        m = folium.Map(location=area_coords, zoom_start=13)

        # Add hospital markers to the map
        for _, row in nearby_hospitals.iterrows():
            hospital_coords = (row['latitude'], row['longitude'])
            popup_text = f"<br>{row['Paragraphs']}<br><a href='{row['URL']}'>Website</a>"
            folium.Marker(location=hospital_coords, popup=popup_text).add_to(m)

        # Sidebar list of nearby properties and analysis
        st.sidebar.header("Nearby Properties and Analysis")
        for _, row in nearby_hospitals.iterrows():
            st.sidebar.write(f"Property: {row['Property Name']} - Popularity Index: {row['Population Index']}")

        # Display the map
        st.write(f"Hospitals with {selected_specialty} specialty within 5 km of {selected_area}:")
        folium_static(m)