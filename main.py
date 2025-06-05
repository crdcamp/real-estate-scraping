import requests
from bs4 import BeautifulSoup

def find_tables(url):
    # Send request and parse HTML
    r = requests.get(url)
    print(f'Status code = {r.status_code}\n')
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find tables
    tables = {
        'DetailData': soup.find('table', class_='DetailData'),
        'ValueData': soup.find('table', class_='ValueData'),
        'ImpData': soup.find('table', class_='ImpData'),
        'LandData': soup.find('table', class_='LandData')
    }

    # Function to extract data from a table cell
    def extract_cell_data(table, label):
        if not table:
            print(f"{label} table not found")
            return None
        cell = table.find('td', string=lambda text: text and label in text.strip())
        if cell:
            next_cell = cell.find_next('td')
            if next_cell:
                return next_cell.text.strip()
            print(f"{label} value cell not found")
        else:
            print(f"{label} cell not found")
        return None

    # Function to process a table and extract multiple fields
    def process_table(table, table_name, labels):
        if table:
            print(f"Found {table_name}\n")
            results = {}
            for label, display_name in labels:
                value = extract_cell_data(table, label)
                if value is not None:  # Allow empty strings
                    results[display_name] = value
                    print(f"{display_name}: {value}")
            return results
        else:
            print(f"{table_name} not found")
            return {}

    # Define labels to extract from DetailDataTable
    detail_labels = [
        ('Property Desc:', 'Property Description'),
        ('Phys. Address:', 'Physical Address'),
        ('Primary:', 'Primary Ownership'),
        ('Secondary:', 'Secondary Ownership'),
        ('C/O', 'Mailing Address - C/O'),
        ('Addr.', 'Address'),
        ('CSZ', 'Address - CSZ'),
        ('Sale Date', 'Most Recent Sale Date')
    ]

    # Process DetailDataTable
    process_table(tables['DetailData'], 'DetailDataTable', detail_labels)

find_tables('https://gis.summitcountyco.gov/map/DetailData.aspx?Schno=6507888')