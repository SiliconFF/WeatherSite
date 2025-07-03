import requests
import gzip
import io
from PIL import Image
from bs4 import BeautifulSoup
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_drive():
    """Authenticate using a service account and return a Google Drive service object."""
    # Load credentials from the service account JSON key file
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    # Build the Google Drive API service
    service = build('drive', 'v3', credentials=creds)
    return service

service = authenticate_drive()



while (True):

    html_raw = requests.get('https://mrms.ncep.noaa.gov/RIDGEII/L2/CONUS/CREF_QCD/').text

    soup = BeautifulSoup(html_raw, 'html.parser')

    tableData = soup.find('table')

    links = tableData.find_all('a')
    links = links[len(links)-1:len(links)]
    i=0
    for link in links:
        url = 'https://mrms.ncep.noaa.gov/RIDGEII/L2/CONUS/CREF_QCD/'+link.get('href')
        print(url)

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch file: {response.status_code}")

        # Step 2: Extract the TIFF file from the gzip content
        gzip_bytes = io.BytesIO(response.content)
        with gzip.GzipFile(fileobj=gzip_bytes, mode='rb') as gz:
            tiff_data = gz.read()

        # Step 3: Convert TIFF to PNG
        # Load the TIFF data into a PIL Image object
        tiff_io = io.BytesIO(tiff_data)
        image = Image.open(tiff_io)

        # Save the image as PNG
        output_path = f"radar{i}.png"
        image.save(output_path, format="PNG")
        i+=1
    file_id = '1qTscTebAOOIK99Wu7WwwJyRxLDTgiMHy'
    file_path = 'radar0.png'  #Local file
    file_name = 'radar0.png'  # Name of the file in Google Drive
    mime_type='image/png'
    media = MediaFileUpload(file_path, mimetype=mime_type)
    # Upload the file
    file = service.files().update(
        media_body=media,
        fileId=file_id,
        fields='id, name'
    ).execute()
    
    print(f"File updated. ID remains: {file['id']}")
    time.sleep(30)


