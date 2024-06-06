# download latest integration version - currently getting 423 error possibly because an integration we want to extract is being edited or is locked

import os
import requests
from datetime import datetime

# Replace these variables with your Oracle Integration Cloud details
OIC_INSTANCE = 'OIC INSTANCE'
OIC_USERNAME = 'USERNAME'
OIC_PASSWORD = 'PASSWORD'

# Set up session for persistent connection with authentication
session = requests.Session()
session.auth = (OIC_USERNAME, OIC_PASSWORD)

# API endpoint to retrieve integration IDs with a specific name pattern
integrations_url = f'https://{OIC_INSTANCE}/ic/api/integration/v1/integrations?q={{name:/INT_/}}'

# Local directory to save exported IAR files
# Change this to your local DOWNLOAD directory
export_directory = os.path.expanduser('~/Downloads')

# Generate current date for use in file names
current_date = datetime.now().strftime('%Y%m%d')

# File path for the exported integrations info text file
exported_info_filename = f'exported_integrations_info_{current_date}.txt'
exported_info_filepath = os.path.join(export_directory, exported_info_filename)

# Dictionary to store the latest version for each integration code
latest_versions = {}

try:
    # Make the request to retrieve integration data
    response = session.get(integrations_url)
    response.raise_for_status()

    # Parse the response content as JSON
    integration_data = response.json()

    # Get the current download date
    download_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Open the text file for writing
    with open(exported_info_filepath, 'w') as exported_info_file:
        # Write header to the text file
        exported_info_file.write("Code Name | Integration Version | Status | Download Date\n")

        # Extract and export the latest version of integrations with names starting with 'INT_'
        for integration in integration_data.get('items', []):
            if integration['name'].startswith('INT_'):
                # Extract integration code, version, and status
                integration_code = integration['code']
                integration_version = integration['version']
                integration_status = integration['status']

                # Check if a version is found or if the current version is newer
                if integration_code not in latest_versions or integration_version > latest_versions[integration_code]:
                    # Update the latest version in the dictionary
                    latest_versions[integration_code] = integration_version

                    # Write information to the text file
                    exported_info_file.write(
                        f"{integration_code} | {integration_version} | {integration_status} | {download_date}\n")

                    # Composite identifier {id} for export API
                    integration_id = f"{integration_code}|{integration_version}"

                    # API endpoint for exporting integration
                    export_url = f'https://{OIC_INSTANCE}/ic/api/integration/v1/integrations/{integration_id}/archive'

                    # Make the request to export the integration
                    export_response = session.get(export_url)
                    export_response.raise_for_status()

                    # Save the exported IAR file to the local directory
                    iar_filename = f"{integration_code}_{integration_version}.iar"
                    iar_filepath = os.path.join(export_directory, iar_filename)

                    with open(iar_filepath, 'wb') as iar_file:
                        iar_file.write(export_response.content)

                    print(f"Integration {integration_id} exported to {iar_filepath}")

    print(f"Exported integrations info saved to {exported_info_filepath}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

finally:
    # Close the session
    session.close()