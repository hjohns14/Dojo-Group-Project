import googlemaps

apikey = "AIzaSyBrDzRBHS7sBuOr2wOUVMCiILy2OBYO9t4"

def getmapembed(address):
    try:
        gmaps = googlemaps.Client(key=apikey)
        address = str(gmaps.geocode(address)[0]["formatted_address"]).replace(" ","+")
        return "https://www.google.com/maps/embed/v1/place?key=" + apikey + "&q=" + address

    except Exception:
        return ""