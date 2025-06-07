import requests
from bs4 import BeautifulSoup

def confirm_document_content(url):
    r = request.get(url)

def find_tables(url):
    # Send request and parse HTML
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find tables
    tables = {
        'DetailData': soup.find('table', class_='DetailData'),
    }

    # Function to extract data from a table cell
    def extract_cell_data(table, label):
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
        ('Property Desc:', 'Property Description')
    ]

    # Process DetailDataTable
    process_table(tables['DetailData'], 'DetailDataTable', detail_labels)

find_tables('https://gis.summitcountyco.gov/map/DetailData.aspx?Schno=6507888')