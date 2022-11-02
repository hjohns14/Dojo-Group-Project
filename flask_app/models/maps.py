#run "pipenv install googlemaps"
import googlemaps
import os
from dotenv import load_dotenv
load_dotenv()


apikey = os.getenv("maps_api")

def getmapembed(address):
    try:
        gmaps = googlemaps.Client(key=apikey)
        address = str(gmaps.geocode(address)[0]["formatted_address"]).replace(" ","+")
        return "https://www.google.com/maps/embed/v1/place?key=" + apikey + "&q=" + address

    except Exception:
        return ""