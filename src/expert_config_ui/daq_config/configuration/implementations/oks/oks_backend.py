"""
Manages the configuration of the OKS backend for the DAQ system.
"""

from typing import Optional

from expert_config_ui.daq_config.configuration.implementations.oks.oks_class import OksKernelClassHandler

from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import (
    IConfigBackend,
)
from expert_config_ui.daq_config.configuration.implementations.oks.oks_kernel import OksKernelConfiguration

class OksKernelBackend(IConfigBackend[OksKernelClassHandler]):
    """
    Handles the backend operations for the OKS configuration management.
    This class initializes the OKS kernel configuration and provides methods to interact with it.
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        super().__init__()
        self._CONFIGURATION = OksKernelConfiguration()

        if config_path:
            self._CONFIGURATION.open_configuration(config_path)

        # For handling class properties
        self._PROPERTY_HANDLER = OksKernelClassHandler(self._CONFIGURATION)
        
