'''
Allows for the interaction with schema and data.
'''

from expert_config_ui.daq_config.configuration.implementations.conffwk.conffwk_backend import ConffwkBackend
from expert_config_ui.daq_config.configuration.implementations.oks.oks_backend import OksKernelBackend
from expert_config_ui.daq_config.configuration.implementations.oks.oks_class import OksKernelClassHandler
import conffwk

'''
Defines a set of classes for interacting with schema and data in the context of DAQ configuration.
'''

class SchemaClassNotFoundError(Exception):
    '''
    Exception raised when a schema class is not found.
    '''
    def __init__(self, message: str):
        super().__init__(message)
        
class CorruptedSchemaError(Exception):
    '''
    Exception raised when a schema is corrupted.
    '''
    def __init__(self, message: str):
        super().__init__(message)
        
class SchemaDataClassInteraction:
    '''
    Allows for changes to be prop
    '''
    def __init__(self, conffwk_class: conffwk.dal, oks_class_handler: OksKernelClassHandler):
        self.conffwk_class = conffwk_class
        self.oks_class_handler = oks_class_handler

class SchemaDataInteraction:
    def __init__(self, conffwk_backend: ConffwkBackend, oks_kernel_backend: OksKernelBackend):
        '''
        Initializes the SchemaDataInteraction with the provided backends.
        
        :param conffwk_backend: An instance of ConffwkBackend for configuration framework interactions.
        :param oks_kernel_backend: An instance of OksKernelBackend for OKS kernel interactions.
        '''
        self.conffwk_backend = conffwk_backend
        self.oks_kernel_backend = oks_kernel_backend
    