import csv

import requests
from bs4 import BeautifulSoup

headers = {
    "Referer": "https://www.westside.com/",
}


def get_store_links(page):
    url = "https://customapp.trent-tata.com/api/custom/getstore-all"
    params = {"type": "Westside", "page": page}
    response = requests.get(url, headers=headers, params=params)
    print(response.url)
    soup = BeautifulSoup(response.json().get('data'), "html.parser")
    store_links = soup.find_all("a", {"class": "moredetails"})
    return list(map(lambda x: x.attrs.get('href'), store_links))

# Create a CSV file to store the extracted data
with open("store_location.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # Write the headers to the CSV file
    writer.writerow(
        ["Store Name", "Address", "Timings", "Latitude", "Longitude", "Phone Number"]
    )

    # Loop through each location and extract the required information
    for page in range(1, 15):
        stores = get_store_links(page)
        print('Page: ', page, 'Stores: ', len(stores))
        for store_url in stores:
            store_html = requests.get(
                store_url,
                headers=headers,
            ).text
            store_content = BeautifulSoup(store_html, "html.parser")
            store_detail_span = store_content.find_all("span", {"class": "storedata"})
            data = {}
            for store_property in store_detail_span:
                text = store_property.get_text()
                text = text.replace(',', ';')
                if 'address' in text.lower():
                    data['address'] = text.split(':')[1].strip()
                    data['store_name'] = data['address'].split(';')[0]
                elif 'phone' in text.lower():
                    data['phone_number'] = text.split(':')[1].strip()
                elif 'opening hours' in text.lower():
                    data['timings'] = text.split('-')[-1].strip()
            map_div = store_content.find("div", {"class": "google_map"})
            iframe_src = map_div.find("iframe").attrs.get('src')
            try:
                data['latitude'] = iframe_src.split('!3d')[1].split('!')[0]
                data['longitude'] = iframe_src.split('!2d')[1].split('!')[0]
            except:
                data['latitude'] = 'N/A'
                data['longitude'] = 'N/A'

            # Write the extracted data to the CSV file
            writer.writerow(
                [
                    data['store_name'],
                    data['address'],
                    data['timings'],
                    data['latitude'],
                    data['longitude'],
                    data['phone_number'],
                ]
            )
