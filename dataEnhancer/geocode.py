"""
Geocode Module

Open StreetMap (Map Features)
http://wiki.openstreetmap.org/wiki/Map_Features
"""
###################################################################################################
#IMPORTS
###################################################################################################
import sys
import json
import os

# Geocoding
from geopy.geocoders import Nominatim
from geopy.exc       import GeocoderTimedOut

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class Geocode:
    """
    Geocode Class
    """
    (NORTH_AMERICA, SOUTH_AMERICA, EUROPE, ASIA, AFRICA, OCEANIA) =('NA', 'SA', 'EU', 'AS', 'AF', 'OC')

    def __init__(self):
        self.__geolocator   = Nominatim()
        self.__geolocator.structured_query_params.add('countrycodes')
        # Load Country Codes
        jsonPath            = os.getcwd()[:-8] + "/tools/countryCodes.json"
        self.__countryCodes = json.loads(open(jsonPath).read())

    ##################################################
    #Private Methods
    ##################################################
    @staticmethod
    def __isValid(gpeInfo):
        """
        Analyze if the GPE is a valid location
        """
        isValid = False
        if gpeInfo:
            if   'boundary' in gpeInfo.raw['class']:
                isValid = True
            elif 'place'    in gpeInfo.raw['class']:
                isValid = True

        return isValid

    def __getCountries(self, continent):
        countries = ''
        for country in self.__countryCodes:
            if country['Cont'] == continent:
                countries += '{0},'.format(country['Code'])

        return countries[:-1]


    ##################################################
    #Public Methods
    ##################################################
    def GetGPE(self, gpeName, gpeContinent):
        """
        Generates an GPE Dict.

        :Parameters:
        - `gpeName`: Geo-Political Entity Name. (Str)
        """
        gpe = None
        try:
            countries = self.__getCountries(gpeContinent)
            query     = {'city':gpeName, 'countrycodes':countries }
            location  = self.__geolocator.geocode(query, geometry='geojson')

            #Find a Boundary or a Place Location Class
            if self.__isValid(location):
                gpe = { gpeName : { 'location':location.address,
                                    'latitude':location.latitude,
                                    'longitude':location.longitude,
                                    'geojson':location.raw['geojson']  } }
        except GeocoderTimedOut:
            pass
        except:
            print("Unexpected error:", sys.exc_info()[0], file=sys.stderr)

        return gpe

    @staticmethod
    def GetFeatureCollection(gpeList):
        """
        Generates an Feature Collection.

        :Parameters:
        - `gpeList`: Geo-Political Entities. (List)
        """
        features        = []
        for city, value in gpeList.items():
            if 'Feature' not in value['geojson']['type']:
                feature = {'type' : 'Feature',
                           'geometry'  :   value['geojson'],
                           'properties': { 'name'     :city,
                                           'location' :value['location'],
                                           'latitude' :value['latitude'],
                                           'longitude':value['longitude'] } }
                features.append(feature)
            else:
                features.append(value['geojson'])
        #Generate a FeatureCollection GeoJSON
        features = {'type':'FeatureCollection',
                    'features': features }

        return features
###################################################################################################
#TEST
###################################################################################################

###################################################################################################
#MAIN
###################################################################################################
if __name__ == "__main__":
    """
    MAIN
    """
    geolocator = Geocode()
    geolocator.GetGPE("Guadalajara", Geocode.NORTH_AMERICA)

###################################################################################################
#END OF FILE
###################################################################################################
