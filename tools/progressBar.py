"""
Progress Bar module
"""
###################################################################################################
#IMPORTS
###################################################################################################
import time

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class ProgressBar:
    """
    Progress Bar Class
    """

    def __init__(self, total, prefix='', decimals=1, length=50, fill='█'):
        """
        :Parameters:
        - `total`: Total iterations (Int)
        - `prefix` (optional): Prefix string (Str)
        - `suffix` (optional): Suffix string (Str)
        - `decimals` (optional): Positive number of decimals in percent complete (Int)
        - `length` (optional): Character length of bar (Int)
        - `fill` (optional): Bar fill character (Str)
        """
        self.__total     = total
        self.__tStamp    = time.clock() #Start time (Int)
        self.__prefix    = prefix
        self.__decimals  = decimals
        self.__length    = length
        self.__fill      = fill
        self.__iteration = 0

    def updateProgress(self):
        """
        Call in a loop to create terminal progress bar

        :Parameters:
        - `iteration`: Current iteration (Int)

        :Returns:
        """
        if  self.__iteration < self.__total:
            self.__iteration += 1
            percent = ("{0:." + str(self.__decimals) + "f}").format(100 * (self.__iteration / float(self.__total)))
            filledLength = int(self.__length * self.__iteration // self.__total)
            progress = self.__fill * filledLength + '-' * (self.__length - filledLength)
            timeStamp = time.clock() - self.__tStamp
            print('\r%s |%s| %s%% - %.3fs - %d of %d' % (self.__prefix, progress, percent, timeStamp, self.__iteration, self.__total), end = '\r')
        # Print New Line on Complete
        elif self.__iteration == self.__total:
            print()


###################################################################################################
#TEST
###################################################################################################
#if __name__ == "__main__":
