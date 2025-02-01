import pandas as pd
import streamlit as st
import folium
from geopy.distance import geodesic
from streamlit_folium import folium_static

# Load the Excel data
data_path = r'C:\Users\BHEL\Desktop\completecomplete.xlsx'
xls = pd.ExcelFile(data_path)
df_population = xls.parse('population_density')
df_plot = xls.parse('plot_details')
df_hospitals = xls.parse('hospitals_hyderabad')

# Initialize session state for area and specialty selection
if 'area_selected' not in st.session_state:
    st.session_state.area_selected = None
if 'specialty_selected' not in st.session_state:
    st.session_state.specialty_selected = None

# Calculate population index based on population density and hospital count
def calculate_population_index(pop_density, hospital_count):
    return pop_density / (1 + hospital_count)

# Filter hospitals by area and specialty
def filter_by_area_and_specialty(hospitals, area_name, specialty):
    hospitals = hospitals[hospitals['Speciality'] == specialty]
    area_population = df_population[df_population['Area'] == area_name]
    if not area_population.empty:
        return hospitals
    return pd.DataFrame()

# Filter hospitals within a 3 km radius of specific coordinates
def filter_hospitals_by_distance(hospitals, coords, max_distance_km=3):
    filtered_hospitals = []
    for _, row in hospitals.iterrows():
        hospital_coords = (row['Hospital-atitude'], row['Hospital-longitude'])
        distance = geodesic(coords, hospital_coords).km
        if distance <= max_distance_km:
            filtered_hospitals.append(row)
    return pd.DataFrame(filtered_hospitals)

# Get latitude and longitude for the selected area
def get_lat_long_from_area(data, area_name):
    area_data = data[data['Area'] == area_name]
    if not area_data.empty:
        return area_data['Latitude'].values[0], area_data['Longitude'].values[0]
    return None

# Page Navigation
page = st.sidebar.radio("Navigation", ["Menu", "Map"])

if page == "Menu":
    st.title("SafetyLink")
    
    # Area and Specialty Selection
    area_options = df_population['Area'].unique().tolist()
    specialty_options = df_hospitals['Speciality'].unique().tolist()
    
    selected_area = st.selectbox("Select Area", area_options)
    selected_specialty = st.selectbox("Select Hospital Specialty", specialty_options)
    
    # Submit Button
    if st.button("Submit"):
        st.session_state.area_selected = selected_area
        st.session_state.specialty_selected = selected_specialty
        st.session_state.page = "Map"

elif page == "Map":
    # Ensuring area and specialty are selected
    if not (st.session_state.area_selected and st.session_state.specialty_selected):
        st.write("Please go to the Menu page to select an area and specialty.")
    else:
        st.title("Nearby Hospitals and Properties")
        selected_area = st.session_state.area_selected
        selected_specialty = st.session_state.specialty_selected
        
        # Get coordinates for the selected area
        area_coords = get_lat_long_from_area(df_population, selected_area)
        
        if area_coords:
            # Getting the population density for the selected area
            area_population = df_population[df_population['Area'] == selected_area]
            population_density = area_population['Population_Density'].values[0] if not area_population.empty else None
            
            # Filter hospitals by specialty and area
            filtered_hospitals = filter_by_area_and_specialty(df_hospitals, selected_area, selected_specialty)
            st.write("Filtered Hospitals by Area and Specialty:")
            st.write(filtered_hospitals)
            
            # Finding hospitals within a 5 km radius of the selected area
            nearby_hospitals = filter_hospitals_by_distance(filtered_hospitals, area_coords, max_distance_km=5)
            st.write("Nearby Hospitals within 5 km of area:")
            st.write(nearby_hospitals)

            # Map centered on the selected area
            m = folium.Map(location=area_coords, zoom_start=15)

            # Add hospital markers
            for _, row in nearby_hospitals.iterrows():
                hospital_coords = (row['Hospital-atitude'], row['Hospital-longitude'])
                popup_text = f"{row['name']}<br>Specialty: {row['Speciality']}"
                folium.Marker(location=hospital_coords, popup=popup_text).add_to(m)

            # Filter properties within a 3 km radius of the selected area
            nearby_properties = []
            for _, row in df_plot.iterrows():
                property_coords = (row['Latitude'], row['Longitude'])
                distance = geodesic(area_coords, property_coords).km
                if distance <= 3:
                    # Count hospitals within 3 km for each property
                    property_hospitals = filter_hospitals_by_distance(filtered_hospitals, property_coords, max_distance_km=3)
                    hospital_count_around_property = len(property_hospitals)
                    
                    # Calculate population index for each property
                    population_index = calculate_population_index(population_density, hospital_count_around_property)
                    row['Population Index'] = population_index
                    row['Hospital Count'] = hospital_count_around_property
                    nearby_properties.append(row)
            nearby_properties = pd.DataFrame(nearby_properties)

            # Add property markers with population index information
            for _, row in nearby_properties.iterrows():
                property_coords = (row['Latitude'], row['Longitude'])
                popup_text = (
                    f"Property: {row['Paragraphs']}<br>"
                    f"Price: {row.get('H2', 'N/A')}<br>"
                    f"Size: {row.get('H6', 'N/A')}<br>"
                    f"Hospitals Nearby: {row['Hospital Count']}<br>"
                    f"Population Index: {row['Population Index']:.2f}<br>"
                    f"URL: {row.get('URL', 'N/A')}"
                )
                folium.Marker(location=property_coords, icon=folium.Icon(color='green'), popup=popup_text).add_to(m)

            # Sidebar list of nearby properties with population index
            st.sidebar.header("Nearby Properties and Analysis")
            for _, row in nearby_properties.iterrows():
                st.sidebar.write(
                    f"Property: {row['Paragraphs']} - Price: {row.get('H2', 'N/A')} - "
                    f"Size: {row.get('H6', 'N/A')} - Hospitals Nearby: {row['Hospital Count']} - "
                    f"Population Index: {row['Population Index']:.2f} - URL: {row.get('URL', 'N/A')}"
                )

            # Display hospital and property counts
            st.write(f"Total hospitals: {len(df_hospitals)}")
            st.write(f"Hospitals found near {selected_area} for {selected_specialty}: {len(nearby_hospitals)}")
            st.write(f"Nearby Properties: {len(nearby_properties)}")
            folium_static(m)
        else:
            st.write("Coordinates for the selected area could not be retrieved from the dataset.")
