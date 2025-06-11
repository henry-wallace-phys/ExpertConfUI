"""
A set of classses that define the interface for managing configurations in a DAQ system.
"""

from typing import Optional, List, Protocol, Any, runtime_checkable, Dict
from enum import Enum
import logging


class ConfigType(Enum):
    DATA = "data"
    SCHEMA = "schema"
    OTHER = "other"


@runtime_checkable
# *****************************************************************************
class IConfiguration(Protocol):
    # *****************************************************************************
    """
    Abstract base class for managing configurations in a DAQ system.
    """
    _configuration: Optional[object] = None
    _configuration_name: Optional[str] = None

    def open_configuration(self, config: Any) -> None:
        """
        Open the configuration using the specific framework.
        :param file_name: Name of the configuration file to open.
        """
        ...

    def save_configuration(self, save_message: Optional[str]) -> None:
        """
        Save the current configuration to a file.
        """
        ...

    @property
    def configuration(self) -> Optional[object]:
        """
        Get the current configuration.
        :return: The current configuration object.
        """
        return self._configuration

    @property
    def name(self) -> Optional[str]:
        """
        Get the name of the current configuration.
        :return: The name of the current configuration.
        """
        return self._configuration_name


@runtime_checkable
# *****************************************************************************
class _IObjectManager(Protocol):
    # *****************************************************************************
    """
    Abstract base class for managing objects in a configuration.
    """

    def get_obj(*args, **kwargs) -> object:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        ...

    def get_all_obj(self, object_class: Optional[str | List[str]] = None) -> List[object]:
        """
        Get all objects in the current configuration.
        :param object_class: Optional class filter for the objects to retrieve.
        :return: A list of all objects or filtered objects.
        """
        ...


@runtime_checkable
# *****************************************************************************
class INamedObjectManager(_IObjectManager, Protocol):
    # *****************************************************************************
    """
    Abstract base class for managing objects in a configuration.
    """

    def get_obj(self, object_class: str, object_name: str) -> object:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        ...


@runtime_checkable
# *****************************************************************************
class IClassObjectManager(_IObjectManager, Protocol):
    # *****************************************************************************
    """
    Abstract base class for managing objects in a configuration.
    """

    def get_obj(self, object_class: str) -> object:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        ...


@runtime_checkable
# *****************************************************************************
class IObjectModifier(Protocol):
    # *****************************************************************************
    def set_attr(self, obj: Any, attribute_name: str, attribute_value: Any) -> None:
        """
        Set the value of an attribute of an object in the configuration.
        :param class_name: Class of the object to modify.
        :param attribute_name: Name of the attribute to modify.
        :param attribute_type: Type of the attribute to modify.
        :param kwargs: Additional parameters for the modification.
        """
        ...

    def get_attr(self, obj: Any, attribute_name: str) -> Any:
        """
        Get an attribute of an object in the configuration.
        :param class_name: Class of the object.
        :param attribute_name: Name of the attribute to retrieve.
        :param attribute_type: Type of the attribute to retrieve.
        :return: The value of the requested attribute.
        """
        ...


@runtime_checkable
# *****************************************************************************
class _IObjectLifecycle(Protocol):
    # *****************************************************************************
    """
    Abstract base class for add/renaming/deleting objects in a configuration.
    """

    def add(self, obj: object) -> None:
        """
        Add an object to the current configuration.
        :param object: The object to add to the configuration.
        """
        ...

    def delete(self, obj: object) -> None:
        """
        Remove an object from the configuration.
        :param object_class: Class of the object to remove.
        :param object_name: Name of the object to remove.
        """
        ...

    def rename(self, obj: object, new_name: str) -> None:
        """
        Add an object to the current configuration by name.
        :param class_name: Class
        of the object to add.
        :param object_name: Name of the object to add.
        :param attributes: Attributes of the object to add.
        """
        ...

    def create(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented in subclasses.")


@runtime_checkable
# *****************************************************************************
class INamedObjectLifecycle(_IObjectLifecycle, Protocol):
    # *****************************************************************************
    def create(
        self, object_class: str, object_name: "str", attributes: Dict[str, Any]
    ) -> None:
        """
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param object_name: Arguments for the object creation.
        :param kwargs: Additional parameters for the object creation.
        """
        ...


@runtime_checkable
# *****************************************************************************
class IClassObjectLifecycle(_IObjectLifecycle, Protocol):
# *****************************************************************************
    def create(self, object_class: str, attributes: Dict[str, Any]) -> None:
        """
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param object_name: Arguments for the object creation.
        :param attributes: Attributes for the object creation.
        """
        ...

"""
Base class for managing interactions with configurations in a DAQ system.
"""
# *****************************************************************************
class ConfigurationInteractionBase:
    # *****************************************************************************
    """
    Base class for managing interactions with configurations in a DAQ system
    """
    __CONFIG_NAME_EXTENSION = ".xml"

    def __init__(self, config_type: ConfigType, configuration: IConfiguration):
        """
        Initialize the Configuration object.
        :param config_type: Type of the configuration (data or schema).
        :param configuration: Optional configuration object to use.
        """
        self._config_type = config_type

        if not str(configuration.name).endswith(
            f"{config_type.name.lower()}{self.__CONFIG_NAME_EXTENSION}"
        ):
            logging.exception(
                f"Configuration name must end with '{config_type.name.lower()}{self.__CONFIG_NAME_EXTENSION}'"
            )

        self._configuration = configuration

    @property
    def configuration(self) -> Optional[IConfiguration]:
        """
        Get the current configuration.
        :return: The current configuration object.
        """
        return self._configuration

    @property
    def config_type(self) -> ConfigType:
        """
        Get the type of the configuration.
        :return: The type of the configuration (data or schema).
        """
        return self._config_type

