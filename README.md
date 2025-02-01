# **Hospital and Prperty locator system**
## Overview
The uneven distribution of hospitals leads to inequitable access to healthcare services, especially in underserved areas.

This project aims to utilize geolocational data to identify optimal locations for new hospitals based on population density and demand.

By providing actionable insights for policymakers, the project seeks to enhance healthcare accessibility and improve patient outcomes, ultimately promoting health equity in communities.

## Datasets Used

**complete excel.xlsx**: The primary dataset containing information on properties, population density, and hospital details.<br/>
**scraped_links.xlsx**: Contains links to individual property listings.<br/>
**population_density_data.xlsx**: Includes area names, latitude, longitude, and population density data.<br/>
**hospitals_hyderabad.xlsx**: Lists hospitals in Hyderabad with their latitude, longitude, and specialty.<br/>

## Code Modules

**Hospitals.py**: Scrapes hospital data from OpenStreetMap.<br/>
**Lat_long_conversion.py**: Converts property addresses to latitude/longitude for mapping.<br/>
**Plots.py**: Scrapes property details from floortap.com.<br/>
**scratch.py**: Manages the user interface, generating the menu page and interactive map.<br/>
**floortap.py**: Scrapes property data from floortap.com to support hospital location analysis.<br/>

## How It Works
1.**Hospital & Population Data Processing**

&ensp;The project utilizes hospital locations and population density to assess demand.<br/>
&ensp;Specialty-based filtering allows users to search for specific hospital types.<br/>

2.**Mapping & Distance Calculations**

&ensp;User selects an area and hospital specialty.<br/>
&ensp;Hospitals within a 5 km radius of the selected area are displayed.<br/>
&ensp;Properties within a 3 km radius of the area are analyzed for population index.<br/>

3.**Property Analysis**

&ensp;Each property is evaluated based on proximity to hospitals and population density.<br/>
&ensp;Population Index = Population Density / (1 + Hospital Count)<br/>
&ensp;Properties are ranked based on accessibility and healthcare availability.<br/>
