# Import Libraries
import random
import folium
import requests

# Constants
LAT_LOWER = 31.3334
LAT_UPPER = 36.9989
LONG_LOWER = -114.8141
LONG_UPPER = -109.0451
API_ENCODING = "Basic [Encoded for use here]" # Add your "Encoded for use" token found on https://wigle.net/account here

def searchSSID(query, map) :
    # Builds search query request url
    urlBase = "https://api.wigle.net/api/v2/network/search?ssid="
    urlQuery = query.replace(" ", "%20")
    urlParams = "&region=AZ"
    urlSearchAfter = ""

    markerColor = randomHexColor()

    while True :
        urlFull = urlBase + urlQuery + urlParams + urlSearchAfter
        
        # Initate GET Request
        response = requests.get(urlFull, headers = {'Authorization' : API_ENCODING})

        if response.status_code == 200 :
            results = response.json().get("results", [])
            trilats = [result.get("trilat") for result in results]
            trilongs = [result.get("trilong") for result in results]

            # Plot points on the 
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

# Adds poits to interactive map
def plotPoints(coords, map, tooltip, color="blue") :
    folium.CircleMarker(
        location=coords, 
        radius=3, 
        tooltip=tooltip,
        color=color).add_to(map)
    
# Generates a random hexadecimal color string
def randomHexColor() :
    # Generate random RGB values
    red = random.randint(100,255)
    green = random.randint(100,255)
    blue = random.randint(100,255)

    # Convert RGB values to hexadecimal
    hexColor = "#{:02x}{:02x}{:02x}".format(red, green, blue)

    return hexColor

# Create interactive map
map = folium.Map(location=[(LAT_LOWER+LAT_UPPER)/2,(LONG_LOWER+LONG_UPPER)/2], zoom_start=7)

searchSSID("McDonalds", map)
searchSSID("Test Network", map)
map.save("WigleMap.html")