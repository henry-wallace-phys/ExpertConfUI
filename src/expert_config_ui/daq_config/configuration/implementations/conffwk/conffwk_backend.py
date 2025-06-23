from typing import Optional

from expert_config_ui.daq_config.configuration.implementations.conffwk.conffwk_config import (
    ConffwkConfiguration,
    ConffwkObjectHandler,
)

from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import (
    IConfigBackend,
)

class ConffwkBackend(IConfigBackend[ConffwkObjectHandler]):
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
        self._PROPERTY_HANDLER = ConffwkObjectHandler(self._CONFIGURATION)