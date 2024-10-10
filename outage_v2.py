import requests
import json

# URLs for county geometry and outage details
geometry_url = "https://poweroutage.us/content/geometry/us/countygeometry/florida.json"
outage_url = "https://poweroutage.us/api/web/counties?key=9818916638&countryid=us&statename=Florida"

# Function to calculate a color based on the outage count
def calculate_color(outage_count, max_outage):
    # Normalize the outage count to a range between 0 and 1
    normalized_value = outage_count / max_outage if max_outage > 0 else 0
    # Convert to a color gradient from yellow (low) to red (high)
    r = int(255 * normalized_value)
    g = int(255 * (1 - normalized_value))
    b = 0
    return f"#{r:02x}{g:02x}{b:02x}"

# Fetch county geometry data
geometry_response = requests.get(geometry_url)
county_geometry_data = geometry_response.json()

# Extract county features from the geometry data
county_features = county_geometry_data.get("CountyGeometry", {}).get("Areas", [])

# Fetch county outage details
outage_response = requests.get(outage_url)
outage_data = outage_response.json()["WebCountyRecord"]

# Create a dictionary to map outage details by county name
outage_map = {county["CountyName"].lower(): county for county in outage_data}

# Determine the maximum outage count for color scaling
max_outage = max(county.get("OutageCount", 0) for county in outage_data)

# Initialize the GeoJSON structure
geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

# Loop through the county geometry and add outage details
for feature in county_features:
    # Extract properties directly from the feature
    county_name = feature.get("NAME", "").lower()
    
    # Get the outage data for the current county
    outage_details = outage_map.get(county_name, None)
    
    # Create properties dictionary from feature and add outage details if available
    properties = {
        "GEO_ID": feature.get("GEO_ID"),
        "STATE": feature.get("STATE"),
        "COUNTY": feature.get("COUNTY"),
        "NAME": feature.get("NAME"),
        "LSAD": feature.get("LSAD"),
        "CENSUSAREA": feature.get("CENSUSAREA")
    }

    if outage_details:
        outage_count = outage_details["OutageCount"]
        customer_count = outage_details["CustomerCount"]
        outage_percentage = (outage_count / customer_count) * 100 if customer_count > 0 else 0

        # Add outage data and calculated values to properties
        properties["OutageCount"] = outage_count
        properties["CustomerCount"] = customer_count
        properties["CountyStatus"] = outage_details["CountyStatus"]
        properties["OutagePercentage"] = outage_percentage
        properties["HeatmapColor"] = calculate_color(outage_count, max_outage)
        properties["Label"] = f"{outage_percentage:.2f}% Outage"
    else:
        # Default values for counties with no outages
        properties["OutageCount"] = 0
        properties["CustomerCount"] = 0
        properties["CountyStatus"] = "No Outage"
        properties["OutagePercentage"] = 0.0
        properties["HeatmapColor"] = "#00ff00"  # Green for no outages
        properties["Label"] = "0.00% Outage"
    
    # Create the feature with updated properties
    updated_feature = {
        "type": "Feature",
        "properties": properties,
        "geometry": feature.get("geometry")
    }

    # Add the feature to the GeoJSON
    geojson_data["features"].append(updated_feature)

# Save the combined data to a GeoJSON file
with open("florida_county_outages.geojson", "w") as geojson_file:
    json.dump(geojson_data, geojson_file, indent=2)

print("GeoJSON file created: florida_county_outages.geojson")