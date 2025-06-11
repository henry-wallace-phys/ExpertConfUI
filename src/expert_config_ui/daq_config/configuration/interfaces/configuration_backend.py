from typing import Any, TypedDict, Union
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import IConfiguration, IClassObjectManager, INamedObjectLifecycle, IObjectModifier, INamedObjectManager, IClassObjectLifecycle

# *****************************************************************************

# Define a union type for all possible handlers
HandlerType = Union[
    IClassObjectManager,
    IObjectModifier,
    IClassObjectLifecycle,
    INamedObjectManager,
    INamedObjectLifecycle
]


"""
Generic adaptor interface for configuration management in a DAQ system. Aim is to connect interfaces in configuration_interface.py
"""
class IPropertyHandler(TypedDict):
    ...

# *****************************************************************************
class IConfigBackend:
    # *****************************************************************************
    """
    Interface for configuration adapters in a DAQ system.
    Provides interfaces for managing configurations, objects, and their properties.
    """

    def __init__(self) -> None:
        """
        Initialize the configuration backend with an empty property handlers dictionary.
        """
        self._PROPERTY_HANDLERS: IPropertyHandler
        self._CONFIGURATION: IConfiguration

    def get_handler(self, handler_type: str) -> HandlerType:
        """
        Get a handler for a specific type of configuration management.
        :param handler_type: Type of the handler to retrieve.
        :return: Handler instance for the specified type.
        """
        if handler_type.lower() not in self._PROPERTY_HANDLERS.keys():
            raise ValueError(f"Handler type '{handler_type}' is not registered.")
        return self._PROPERTY_HANDLERS[handler_type]

    @property
    def property_handlers(self) -> IPropertyHandler:
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

    def register_handler(self, handler_type: str, handler: Any) -> None:
        """Register a new handler type"""
        if handler_type in self._PROPERTY_HANDLERS:
            raise ValueError(f"Handler type '{handler_type}' already registered")
        self._PROPERTY_HANDLERS[handler_type] = handler
