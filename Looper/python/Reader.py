''' Class for a Reader of an instance of Sample.
'''

# Standard imports
import ROOT
import uuid
import copy
import os

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperBase import LooperBase

class Reader( LooperBase ):

    def __init__(self, sample, scalars, vectors, selectionString = None):

        super(Reader, self).__init__( sample = sample, scalars = scalars, vectors = vectors , selectionString = selectionString )

    def run(self):
        ''' Load event into self.entry. Return 0, if last event has been reached
        '''
        if self.position < 0:
            logger.debug("Starting Reader for sample %s", self.sample.name)
            self.initialize()
            self.position = 0
        else:
            self.position += 1
        if self.position == self.nEvents: return 0

        if (self.position % 1000)==0:
            logger.info("Reader for sample %s is at position %6i/%6i", self.sample.name, self.position, self.nEvents)

        # point to the position in the chain (or the eList if there is one)
        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry(self.position)

        return 1
