from typing import Any
from configuration_interface import IConfiguration
# *****************************************************************************

'''
Generic adaptor interface for configuration management in a DAQ system. Aim is to connect interfaces in configuration_interface.py
'''



# *****************************************************************************
class IConfigBackend:
# *****************************************************************************
    """
    Interface for configuration adapters in a DAQ system.
    Provides interfaces for managing configurations, objects, and their properties.
    """
    _PROPERTY_HANDLERS = {}
    _CONFIGURATION: IConfiguration

    def get_handler(self, handler_type: str) -> Any:
        """
        Get a handler for a specific type of configuration management.
        :param handler_type: Type of the handler to retrieve.
        :return: Handler instance for the specified type.
        """
        if handler_type.lower() not in self._PROPERTY_HANDLERS.values():
            raise ValueError(f"Handler type '{handler_type}' is not registered.")
        return self._PROPERTY_HANDLERS[handler_type]

    @property
    def property_handlers(self) -> dict[str, Any]:
        """
        Get the dictionary of registered property handlers.
        :return: Dictionary of property handlers.
        """
        return self._PROPERTY_HANDLERS

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
        
    def save(self, commit_message: str = "") -> None:
        """
        Save the current configuration with an optional commit message.
        :param commit_message: Commit message for the save operation.
        """
        self._CONFIGURATION.save_configuration(commit_message)
        
    def register_handler(self, handler_type: str, handler: Any) -> None:
        """Register a new handler type"""
        if handler_type in self._PROPERTY_HANDLERS:
            raise ValueError(f"Handler type '{handler_type}' already registered")
        self._PROPERTY_HANDLERS[handler_type] = handler