''' Class for a FWLiteReader of an instance of FWLiteSample.
'''

# Standard imports
import ROOT
import os

#FWLite and CMSSW tools
from DataFormats.FWLite import Events, Handle
from PhysicsTools.PythonAnalysis import *

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.core.LooperBase import LooperBase
from RootTools.fwlite.FWLiteSample import FWLiteSample
import RootTools.core.helpers as helpers
from RootTools.core.helpers import shortTypeDict

class FWLiteReader( LooperBase ):

    def __init__(self, sample, products):

        # The following checks are 'look before you leap' but I rather have the user know if the input non-sensical
        if not isinstance(sample, FWLiteSample):
            raise ValueError( "Need instance of FWLiteSample to initialize any Looper instance. Got %r."%sample )
        self.sample = sample

        # Check products
        if not type(products) == type({}):
            raise ValueError( "Argument 'products' must be dictionary: { ..., 'productName':{'label':(x,y,z), 'type':type}, ...}. Got %r."%products )

        for name, product in products.iteritems():
            if not type(name)==type("") or not type(product)==type({}) or not 'type' in product.keys() or not 'label' in product.keys():
                raise ValueError("Product %s:%s not in the correct form. Need 'productName':{'label':(x,y,z), 'type':type}."%(name, product) )
        # Inputs
        self.__products = products
        # Outputs
        self.products = None

        # Create Handles for __products
        self.handles={v:Handle(self.__products[v]['type']) for v in self.__products.keys()}

        # Initialize looper, no TTree variables 
        super(FWLiteReader, self).__init__( variables = [] ) 

        logger.debug("Initializing FWLiteReader for sample %s", self.sample.name)

        self.nEvents = self.sample.events.size()
        logger.debug("Found %i events to in  %s", self.nEvents, self.sample.name)

        #  default event range of the reader
        self.eventRange = (0, self.nEvents)

    def getProducts(self):
        ''' Read all products from the event
        '''
        for name in self.__products.keys():
            self.sample.events.getByLabel(self.__products[name]['label'], self.handles[name])
        self.products = {name: self.handles[name].product() for name in self.__products.keys()}

    def _initialize(self):
        ''' This method is called from the Base class start method.
            Initializes the reader, sets position to lower event range.
        '''
        self.evt = (-1,-1,-1) 
        self.position = 0
        return

    def _execute(self, readProducts = True):  
        ''' Does what a FWLite reader should do: Go to self.position and read the products.
            Returns 0 if upper eventRange is hit. 
        '''
        if self.position == self.eventRange[1]: return 0
        if self.position==0:
            logger.info("FWLiteReader for sample %s starting at position %i and processing %i events.", 
                self.sample.name, self.position, self.eventRange[1] - self.eventRange[0])
        elif (self.position % 10000)==0:
            logger.info("FWLiteReader for sample %s is at position %6i/%6i", 
                self.sample.name, self.position, self.eventRange[1] - self.eventRange[0] )

        # Move to event
        self.sample.events.to(self.position)

        # Get run:lumi:event
        eaux     = self.sample.events.eventAuxiliary()
        self.evt = (eaux.run(), eaux.luminosityBlock(), eaux.event() )
            
        # read all products
        if readProducts:
            self.getProducts() 
        else:
            self.products = None 

        return 1

    def goToPosition(self, position):
        ''' Go to specific positon
        '''
        self.position = position
        self._execute()
