import requests
import json

# Define the ArcGIS REST API endpoint for the Schedule text layer (ID: 12)
url = "https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/12/query"

# Define the list of fields to query
fields = [
    "OBJECTID", "PPI", "EcoDesc", "SubName", "Filing", "ShortDesc", "HouseNum",
    "FullStreet", "StreetName", "TownCode", "TownName", "OwnerAdd1", "OwnerAdd2",
    "OwnerCity", "OwnerState", "PostCode", "FullAdd", "TotAcres", "TotSqFt",
    "MiscChar", "MiscCharID", "NumUnits", "YearBuilt", "SquareFeet", "SqeFtLiving",
    "Unfinished", "BsmtType", "GarageType", "NumOfCars", "GarSqFt", "NumOfRms",
    "NumBedRms", "NumLofts", "NumKitch", "MasterBath", "FullBath", "TqtrBaths",
    "HalfBaths", "QtrBaths", "TotBath", "MobHtitle", "FloorLevel"
]

# Initialize variables for pagination
all_features = []
batch_size = 1000  # Match MaxRecordCount
offset = 0
params = {
    "where": "1=1",  # Return all records
    "outFields": ",".join(fields),  # Retrieve specified fields
    "f": "json",  # Output format as JSON
    "returnGeometry": "false",  # Exclude geometry
    "outSR": "102654",  # Spatial reference
    "resultRecordCount": batch_size  # Number of records per request
}

try:
    while True:
        # Update offset for pagination
        params["resultOffset"] = offset
        
        # Send GET request
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Check for features
        if "features" not in data or not data["features"]:
            break
            
        # Add features to collection
        all_features.extend(data["features"])
        
        # Check if more records exist
        if len(data["features"]) < batch_size:
            break
            
        # Increment offset
        offset += batch_size
    
    # Save all features to JSON file
    if all_features:
        output_data = {
            "displayFieldName": data.get("displayFieldName", ""),
            "fieldAliases": data.get("fieldAliases", {}),
            "fields": data.get("fields", []),
            "features": all_features
        }
        
        # Extract unique PPIs
        total_ppis = set()
        for feature in all_features:
            ppi = feature.get("attributes", {}).get("PPI")
            if ppi is not None:
                total_ppis.add(ppi)
        
        print(f"Total Unique PPIs: {len(total_ppis)}")
        
        with open("schedule_fields_data.json", "w") as f:
            json.dump(output_data, f, indent=2)
        print("Data saved to 'schedule_fields_data.json'")
    else:
        print("No features found in the response.")
        
except requests.exceptions.RequestException as e:
    print(f"Error querying the ArcGIS service: {e}")
except ValueError as e:
    print(f"Error parsing JSON response: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")