'''
Manages the configuration of the OKS backend for the DAQ system.
'''

from oks_class import (OksKernelClassHandler)

from oks_class_properties import (OksClassProperties,
                                    OksKernelAttributeHandler,
                                    OksKernelRelationshipHandler,
                                    OksKernelMethodHandler)
from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import IConfigurationAdapter

from oks_kernel import OksKernelConfiguration
from typing import Optional

class OksKernelBackend(IConfigurationAdapter):
    '''
    Handles the backend operations for the OKS configuration management.
    This class initializes the OKS kernel configuration and provides methods to interact with it.
    '''
    def __init__(self, config_path: Optional[str])->None:
        super().__init__()
        self._CONFIGURATION = OksKernelConfiguration()
        
        if config_path:
            self._CONFIGURATION.open_configuration(config_path)
            
        # Add backend managers
        
        # For handling class properties
        self._PROPERTY_HANDLERS = {
            "class": OksKernelClassHandler(self.config),
            OksClassProperties.ATTRIBUTE.name : OksKernelAttributeHandler(),
            OksClassProperties.RELATIONSHIP.name : OksKernelRelationshipHandler(),
            OksClassProperties.METHOD.name : OksKernelMethodHandler()
        }
    