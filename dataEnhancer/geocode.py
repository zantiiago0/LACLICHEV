"""
Geocode Module
"""
###################################################################################################
#IMPORTS
###################################################################################################
import sys

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

    def __init__(self):
        self.__geolocator = Nominatim()

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
    ##################################################
    #Public Methods
    ##################################################
    def GetGPE(self, gpeName):
        """
        Generates an GPE Dict.

        :Parameters:
        - `gpeName`: Geo-Political Entity Name. (Str)
        """
        gpe = None
        try:
            location = self.__geolocator.geocode(gpeName, geometry='geojson')

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

###################################################################################################
#END OF FILE
###################################################################################################
