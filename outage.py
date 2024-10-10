import requests
import json
import xml.etree.ElementTree as ET
import zipfile
import os

# URLs for county geometry and outage details
geometry_url = "https://poweroutage.us/content/geometry/us/countygeometry/florida.json"
outage_url = "https://poweroutage.us/api/web/counties?key=9818916638&countryid=us&statename=Florida"

# Function to calculate a color based on the outage percentage
def calculate_color(outage_percentage):
    # From black (0% outage) to yellow (100% outage)
    normalized_value = outage_percentage / 100.0
    r = int(255 * normalized_value)
    g = int(255 * normalized_value)
    b = 0
    alpha = 128  # Set alpha for 50% transparency
    return f"{alpha:02x}{b:02x}{g:02x}{r:02x}"

# Fetch county geometry data
try:
    graph_response = requests.get(geometry_url)
    graph_response.raise_for_status()
    county_geometry_data = graph_response.json()
except requests.RequestException as e:
    print(f"Error fetching county geometry data: {e}")
    county_geometry_data = {}

# Extract county features from the geometry data
county_features = county_geometry_data.get("CountyGeometry", {}).get("Areas", [])

# Fetch county outage details
try:
    outage_response = requests.get(outage_url)
    outage_response.raise_for_status()
    outage_data = outage_response.json()["WebCountyRecord"]
except requests.RequestException as e:
    print(f"Error fetching outage data: {e}")
    outage_data = []

# Create a dictionary to map outage details by county name
outage_map = {county["CountyName"].lower(): county for county in outage_data}

# Initialize the KML structure
kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
document = ET.SubElement(kml, "Document")
name = ET.SubElement(document, "name")
name.text = "Florida County Power Outages"

# Loop through the county geometry and add outage details
for feature in county_features:
    # Extract properties directly from the feature
    county_name = feature.get("NAME", "").lower()

    # Get the outage data for the current county
    outage_details = outage_map.get(county_name, None)

    # Skip counties without outage data or geometry
    if not outage_details:
        print(f"Warning: No outage data for county {county_name}")
        continue
    if not feature.get("geometry"):
        print(f"Warning: No geometry data for county {county_name}")
        continue

    # Extract coordinates from geometry
    geometry = feature.get("geometry")
    if geometry["type"].lower() == "multipolygon":
        # Handle MultiPolygon type with multiple sets of coordinates
        placemark = ET.SubElement(document, "Placemark")
        name = ET.SubElement(placemark, "name")
        name.text = feature.get("NAME", "Unknown")

        # Add description with outage information
        description = ET.SubElement(placemark, "description")
        outage_count = outage_details.get("OutageCount", 0)
        customer_count = outage_details.get("CustomerCount", 0)
        outage_percentage = (outage_count / customer_count) * 100 if customer_count > 0 else 0
        description.text = f"Outage Percentage: {outage_percentage:.2f}%\nOutage Count: {outage_count}\nCustomer Count: {customer_count}"

        # Add style for coloring the polygon based on outage percentage
        style_url = ET.SubElement(placemark, "styleUrl")
        style_url.text = f"#style_{county_name}"

        # Create a single Polygon element to hold all parts
        polygon = ET.SubElement(placemark, "Polygon")
        altitude_mode = ET.SubElement(polygon, "altitudeMode")
        altitude_mode.text = "clampToGround"

        # Loop through each polygon in the MultiPolygon
        for i, polygon_coords in enumerate(geometry["coordinates"]):
            if i == 0:
                # First polygon is the outer boundary
                outer_boundary = ET.SubElement(polygon, "outerBoundaryIs")
                linear_ring = ET.SubElement(outer_boundary, "LinearRing")
                coord_elem = ET.SubElement(linear_ring, "coordinates")
                coord_string = " ".join([f"{coord[0]},{coord[1]},0" for coord in polygon_coords[0]])
                coord_elem.text = coord_string
            else:
                # Subsequent polygons are inner boundaries (holes)
                inner_boundary = ET.SubElement(polygon, "innerBoundaryIs")
                linear_ring = ET.SubElement(inner_boundary, "LinearRing")
                coord_elem = ET.SubElement(linear_ring, "coordinates")
                coord_string = " ".join([f"{coord[0]},{coord[1]},0" for coord in polygon_coords[0]])
                coord_elem.text = coord_string

    elif geometry["type"].lower() == "polygon":
        # Handle Polygon type with coordinates
        placemark = ET.SubElement(document, "Placemark")
        name = ET.SubElement(placemark, "name")
        name.text = feature.get("NAME", "Unknown")

        # Add description with outage information
        description = ET.SubElement(placemark, "description")
        outage_count = outage_details.get("OutageCount", 0)
        customer_count = outage_details.get("CustomerCount", 0)
        outage_percentage = (outage_count / customer_count) * 100 if customer_count > 0 else 0
        description.text = f"Outage Percentage: {outage_percentage:.2f}%\nOutage Count: {outage_count}\nCustomer Count: {customer_count}"

        # Add style for coloring the polygon based on outage percentage
        style_url = ET.SubElement(placemark, "styleUrl")
        style_url.text = f"#style_{county_name}"

        # Create a Polygon element
        polygon = ET.SubElement(placemark, "Polygon")
        altitude_mode = ET.SubElement(polygon, "altitudeMode")
        altitude_mode.text = "clampToGround"
        outer_boundary = ET.SubElement(polygon, "outerBoundaryIs")
        linear_ring = ET.SubElement(outer_boundary, "LinearRing")
        coord_elem = ET.SubElement(linear_ring, "coordinates")
        coord_string = " ".join([f"{coord[0]},{coord[1]},0" for coord in geometry["coordinates"][0]])
        coord_elem.text = coord_string
    else:
        print(f"Debug: Geometry data for county {county_name} does not contain valid 'coordinates': {geometry}")
    
# Define styles for the polygons based on outage percentage
for county_name, outage_details in outage_map.items():
    style = ET.SubElement(document, "Style", id=f"style_{county_name}")
    line_style = ET.SubElement(style, "LineStyle")
    line_color = ET.SubElement(line_style, "color")
    line_color.text = "00000000"  # Transparent line
    line_width = ET.SubElement(line_style, "width")
    line_width.text = "0"
    poly_style = ET.SubElement(style, "PolyStyle")
    poly_color_elem = ET.SubElement(poly_style, "color")
    outage_count = outage_details.get("OutageCount", 0)
    customer_count = outage_details.get("CustomerCount", 0)
    outage_percentage = (outage_count / customer_count) * 100 if customer_count > 0 else 0
    poly_color_elem.text = calculate_color(outage_percentage)

# Write the KML to a file
tree = ET.ElementTree(kml)
kml_path = "florida_county_outages.kml"
with open(kml_path, "wb") as kml_file:
    tree.write(kml_file, encoding="utf-8", xml_declaration=True)

print("KML file created: florida_county_outages.kml")

# Create KMZ from KML
kmz_path = "florida_county_outages.kmz"
with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
    kmz.write(kml_path, os.path.basename(kml_path))
print(f"KMZ file created: {kmz_path}")