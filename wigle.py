# Import Libraries
import requests
import folium
import random
import subprocess
import csv
import time
import os
from selenium import webdriver

# Constants
LAT_LOWER = 31.3334
LAT_UPPER = 36.9989
LONG_LOWER = -114.8141
LONG_UPPER = -109.0451

API_ENCODING = "Basic [Encoded for use here]" # Add your "Encoded for use" token found on https://wigle.net/account here

# Search ESSIDs using Wigle API
def searchSSID(query, map) :
    print("Searching Wigle API for " + query + "...")
    # Builds search query request url
    urlBase = "https://api.wigle.net/api/v2/network/search?ssid="
    urlQuery = query.replace(" ", "%20")
    urlParams = "&region=AZ"
    urlSearchAfter = ""

    markerColor = randomHexColor()

    while True :
        urlFull = urlBase + urlQuery + urlParams + urlSearchAfter
        
        # Initiate GET Request
        response = requests.get(urlFull, headers = {'Authorization' : API_ENCODING})

        if response.status_code == 200 :
            results = response.json().get("results", [])
            trilats = [result.get("trilat") for result in results]
            trilongs = [result.get("trilong") for result in results]

            # Plot points on the map
            for i in range(len(trilats)) :
                plotPoints([trilats[i],trilongs[i]], map, query, markerColor)
            
            # Break if on last page of results
            if int(response.json()["last"]) < 100 :
                break

            # URL for next page of results
            urlSearchAfter = "&searchAfter=" + response.json()["searchAfter"]
            
        else:
            print("Failed \nMessage: %s" %response.json()['message'])
            break

# Read capture file for new ESSIDs
def readRequests(filePath, essids, map, browser):
    foundNew = False
    with open(filePath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            if len(row) > 13:
                essid = row[13].strip()
                # Plot ESSID and add it to the list of found ESSIDs
                if essid and essid not in essids:
                    foundNew = True
                    searchSSID(essid, map)
                    essids.append(essid)
                    time.sleep(2)
    if foundNew:
        map.save("WigleMap.html")
        browser.refresh()

# Adds points to interactive map
def plotPoints(coords, map, tooltip, color="blue") :
    folium.CircleMarker(
        location=coords, 
        radius=3, 
        tooltip=tooltip,
        color=color).add_to(map)
    
# Generates a random hexadecimal color string
def randomHexColor() :
    # Generate random RGB values
    red = random.randint(0,255)
    green = random.randint(0,255)
    blue = random.randint(0,255)

    # Convert RGB values to hexadecimal
    hexColor = "#{:02x}{:02x}{:02x}".format(red, green, blue)

    return hexColor

print(API_ENCODING)

# Remove old capture file
if os.path.exists("capture-01.csv"):
    os.remove("capture-01.csv")

# Create interactive map
map = folium.Map(location=[(LAT_LOWER+LAT_UPPER)/2,(LONG_LOWER+LONG_UPPER)/2], zoom_start=7)
map.save("WigleMap.html")

# Open Map file in Firefox
browser = webdriver.Firefox()
browser.get("file:///home/kali/Desktop/WigleTest/WigleMap.html")
time.sleep(5)

# Start airodump command and save capture
command = ['sudo','airodump-ng','wlan0', '--output-format', 'csv', '-w', 'capture']
process = subprocess.Popen(command, stdout=subprocess.PIPE)

# Array of found ESSIDs
essids = []

# Read capture file every 5 seconds and plot any new points
try:
    while True:
        time.sleep(5)
        readRequests("capture-01.csv", essids, map, browser)
        print("Current essids: " + str(essids))
except KeyboardInterrupt:
    process.terminate()
