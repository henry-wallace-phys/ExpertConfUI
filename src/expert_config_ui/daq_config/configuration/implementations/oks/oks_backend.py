"""
Manages the configuration of the OKS backend for the DAQ system.
"""

from typing import Optional

from expert_config_ui.daq_config.configuration.implementations.oks.oks_class import OksKernelClassHandler
from expert_config_ui.daq_config.configuration.implementations.oks.oks_class_properties import (
    OksClassProperties,
    OksKernelAttributeHandler,
    OksKernelRelationshipHandler,
    OksKernelMethodHandler,
)
from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import (
    IConfigBackend,
    IPropertyHandler
)
from expert_config_ui.daq_config.configuration.implementations.oks.oks_kernel import OksKernelConfiguration

class OksProperties(IPropertyHandler):
    class_obj: OksKernelClassHandler
    attribute: OksKernelAttributeHandler
    relationship: OksKernelRelationshipHandler
    method: OksKernelMethodHandler

class OksKernelBackend(IConfigBackend):
    """
    Handles the backend operations for the OKS configuration management.
    This class initializes the OKS kernel configuration and provides methods to interact with it.
    """

    def __init__(self, config_path: Optional[str]) -> None:
        super().__init__()
        self._CONFIGURATION = OksKernelConfiguration()

        if config_path:
            self._CONFIGURATION.open_configuration(config_path)

        # Add backend managers

        # For handling class properties
        self._PROPERTY_HANDLERS: OksProperties = {
            "class_obj": OksKernelClassHandler(self._CONFIGURATION),
            OksClassProperties.ATTRIBUTE.value: OksKernelAttributeHandler(),
            OksClassProperties.RELATIONSHIP.value: OksKernelRelationshipHandler(),
            OksClassProperties.METHOD.value: OksKernelMethodHandler(),
        }
