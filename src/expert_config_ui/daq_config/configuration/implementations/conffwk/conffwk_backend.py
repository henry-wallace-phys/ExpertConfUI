from expert_config_ui.daq_config.configuration.implementations.conffwk.conffwk_config import (
    ConffwkConfiguration,
    ConffwkObjectHandler,
)

from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import (
    IConfigBackend,
    IPropertyHandler
)
from typing import Optional

class ConffwkProperties(IPropertyHandler):
    """
    Properties handler for Conffwk configurations.
    This class defines the properties that can be managed within the Conffwk framework.
    """
    class_obj: ConffwkObjectHandler
    # Additional properties can be added here as needed

class ConffwkBackend(IConfigBackend):
    """
    Backend for managing configurations using the Conffwk framework.
    This class initializes the Conffwk configuration and provides methods to interact with it.
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        super().__init__()
        self._CONFIGURATION = ConffwkConfiguration()

        if config_path:
            self._CONFIGURATION.open_configuration(config_path)

        # Add backend managers
        self._PROPERTY_HANDLERS: ConffwkProperties = {"class_obj": ConffwkObjectHandler(self._CONFIGURATION)}