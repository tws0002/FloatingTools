"""
Github handler class 
"""
# python imports
import os

# FT imports
from AbstractService import Handler


class LocalHandler(Handler):
    def loadSource(self, source):
        """
        Load a local location on disk.
        :param source: 
        :return: 
        """
        # define as pointer
        self.setIsPointer(True)

        # set vars
        self.setName(os.path.basename(source['Path']))
        self.setInstallLocation(source['Path'])


# add fields
LocalHandler.addSourceField('Path')

# register handler
LocalHandler.registerHandler('Local')