import requests
import gzip
import io
from PIL import Image
from bs4 import BeautifulSoup
import time

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
    output_path = f"radar.png"
    image.save(output_path, format="PNG")
    i+=1

