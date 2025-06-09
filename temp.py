import requests
from datetime import datetime

def get_database_ppis():
    """Retrieve all PPIs from the database (layer 12) for comparison"""
    url = "https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/12/query"
    
    all_features = []
    batch_size = 1000
    offset = 0
    params = {
        "where": "1=1",
        "outFields": "*",  # Get all fields for matching features
        "f": "json",
        "returnGeometry": "false",
        "outSR": "102654",
        "resultRecordCount": batch_size
    }
    
    print("Loading database PPIs for comparison...")
    
    try:
        while True:
            params["resultOffset"] = offset
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "features" not in data or not data["features"]:
                break
                
            all_features.extend(data["features"])
            
            if len(data["features"]) < batch_size:
                break
                
            offset += batch_size
        
        # Create a dictionary mapping PPI to feature data
        ppi_to_feature = {}
        for feature in all_features:
            ppi = feature.get("attributes", {}).get("PPI")
            if ppi is not None:
                ppi_to_feature[ppi] = feature
        
        print(f"Loaded {len(ppi_to_feature)} unique PPIs from database")
        return ppi_to_feature
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying the database: {e}")
        return {}

def main():
    num_results = 5
    
    # Get database PPIs for comparison
    database_ppis = get_database_ppis()
    
    if not database_ppis:
        print("Failed to load database PPIs. Exiting.")
        return
    
    # Query URL with adjustable result count
    query_url = f"https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/19/query?where=SOURCE=1&orderByFields=MODDATE%20DESC&resultRecordCount={num_results}&outFields=*&returnGeometry=false&f=json"
    
    # Send the request
    response = requests.get(query_url)
    if response.status_code == 200:
        data = response.json()
        features = data.get("features", [])
        
        matching_count = 0
        results_json = []  # Store results as raw JSON
        
        # Define field lists at the beginning of the loop
        modtype_fields = [
            'AREA', 'PERIMETER', 'OBJECTID', 'PPI', 'SOURCE', 
            'MODDATE', 'MODTYPE'
        ]
        
        schedule_fields = [
            'OBJECTID_1', 'OBJECTID', 'PPI', 'Schedule', 'EcoCode', 'EcoDesc',
            'NhoodCode', 'NhoodDescr', 'SubCode', 'SubName', 'SecondID', 'ShortDesc',
            'AddressID', 'StreetID', 'SitusAdd', 'HouseNum', 'FullStreet', 'StreetName',
            'TownCode', 'TownName', 'OwnerAdd1', 'OwnerAdd2', 'OwnerCity', 'OwnerState',
            'PostCode', 'FullAdd', 'TotAcres', 'TotSqFt', 'YearBuilt', 'ExtWallMat',
            'ExtWallHgt', 'HeatType', 'SquareFeet', 'SqeFtLiving', 'Unfinished',
            'BsmtType', 'GarageType', 'NumOfCars', 'GarSqFt', 'NumOfRms', 'NumBedRms',
            'NumLofts', 'NumKitch', 'MasterBath', 'FullBath', 'TqtrBaths', 'HalfBaths',
            'QtrBaths', 'TotBath', 'MobHtitle', 'FloorLevel', 'ImpPos'
        ]
        
        for i, feature in enumerate(features, 1):
            attributes = feature.get("attributes", {})
            ppi = attributes.get("PPI")
            mod_date = attributes.get("MODDATE")
            
            # Convert MODDATE (Unix timestamp in milliseconds) to readable date
            if mod_date:
                mod_date_readable = datetime.fromtimestamp(mod_date / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                mod_date_readable = "N/A"
            
            # Only print if PPI exists in database
            if ppi in database_ppis:
                matching_count += 1
                database_feature = database_ppis[ppi]
                database_attributes = database_feature.get("attributes", {})
                
                if matching_count == 1:  # Print header only when first match is found
                    print(f"\nMatching PPIs from Most Recently Modified Parcels:")
                
                print(f"\n--- Match #{matching_count} - PPI: {ppi} ---")
                print(f"Modified Date: {mod_date_readable}")
                
                # Collect match data for JSON storage
                match_data = {
                    'PPI': ppi,
                    'Modified Date': mod_date_readable,
                    'Raw Modified Date': mod_date,
                    'MODTYPE Attributes': {},
                    'Schedule ID Attributes': {}
                }
                
                # Collect MODTYPE attributes
                for field in modtype_fields:
                    if field in attributes:
                        match_data['MODTYPE Attributes'][field] = attributes[field]
                
                # Collect Schedule ID attributes
                for field in schedule_fields:
                    if field in database_attributes:
                        match_data['Schedule ID Attributes'][field] = database_attributes[field]
                
                # Add to results JSON
                results_json.append(match_data)
                
                # Print MODTYPE attributes (from layer 19)
                print("\nMODTYPE ATTRIBUTES:")
                for field in modtype_fields:
                    if field in attributes:
                        value = attributes[field]
                        if field == 'MODDATE' and value:
                            # Convert timestamp for MODDATE display
                            value = datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d %H:%M:%S")
                        print(f"  {field}: {value}")
                
                # Print Schedule ID attributes (from layer 12)
                print("\nSCHEDULE ID ATTRIBUTES:")
                for field in schedule_fields:
                    if field in database_attributes:
                        value = database_attributes[field]
                        print(f"  {field}: {value}")
                
                print("-" * 50)
        
        # Summary
        if matching_count > 0:
            print(f"\nSUMMARY:")
            print(f"Total queried parcels: {len(features)}")
            print(f"Matching PPIs found in database: {matching_count}")
            print(f"Match percentage: {(matching_count/len(features)*100):.1f}%")
            
            # Return the JSON results for further processing
            return results_json
        else:
            print(f"\nNo matching PPIs found in database out of {len(features)} queried parcels.")
            return []
        
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return []

json_results = main()

# Optional: Print the JSON structure for verification
if json_results:
    print(f"\n--- JSON RESULTS SAVED ---")
    print(f"Number of records stored: {len(json_results)}")
    # Uncomment the next line to see the full JSON structure:
    # import json; print(json.dumps(json_results, indent=2))

    schedule_value = json_results[0]['Schedule ID Attributes']['Schedule']

    # To loop through all records and access Schedule:
    for record in json_results:
        schedule = record['Schedule ID Attributes']['Schedule']

    # To get all Schedule values as a list:
        schedules = [record['Schedule ID Attributes']['Schedule'] for record in json_results]

    for id in schedules:
        all_scrape_urls = []
        scrape_url = f'https://gis.summitcountyco.gov/map/DetailData.aspx?Schno={id}'
        requests.get(scrape_url)
        all_scrape_urls.append(scrape_url)
        print(scrape_url)