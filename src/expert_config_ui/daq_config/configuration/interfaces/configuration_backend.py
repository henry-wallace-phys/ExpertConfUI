from typing import Any, TypeVar, Union, Generic
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (IConfiguration,
                                                                                          IObjectModifier,
                                                                                          _IObjectLifecycle,
                                                                                          _IObjectManager)


T = TypeVar('T')

# *****************************************************************************
class IConfigBackend(Generic[T]):
    # *****************************************************************************
    """
    Interface for configuration adapters in a DAQ system.
    Provides interfaces for managing configurations, objects, and their properties.
    """
    _PROPERTY_HANDLER: T
    _CONFIGURATION: IConfiguration
    
    @property
    def handler(self) -> T:
        """
        Get the dictionary of registered property handlers.
        :return: Dictionary of property handlers.
        """
        return self._PROPERTY_HANDLER

    def get_configuration(self) -> IConfiguration:
        """
        Get the current configuration instance.
        :return: Current configuration instance.
        """
        return self._CONFIGURATION

    def open(self, configuration_name: str) -> None:
        """
        Open a configuration by its name.
        :param configuration_name: Name of the configuration to open.
        """
        self._CONFIGURATION.open_configuration(configuration_name)

    def close(self, partial_close: str = "", file_names: Any = None) -> None:
        """
        Close the current configuration.
        :param partial_close: Optional parameter to specify if the close is partial.
        :param file_names: Optional file names to close.
        """
        self._CONFIGURATION.close_configuration(partial_close, file_names)

    def save(self, commit_message: str = "") -> None:
        """
        Save the current configuration with an optional commit message.
        :param commit_message: Commit message for the save operation.
        """
        self._CONFIGURATION.save_configuration(commit_message)
