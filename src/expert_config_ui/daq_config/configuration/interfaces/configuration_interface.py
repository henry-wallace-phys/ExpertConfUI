"""
A set of classses that define the interface for managing configurations in a DAQ system.
"""

from typing import Optional, List, Protocol, Any, runtime_checkable, Dict, Generic, TypeVar, Type
from enum import Enum


# *****************************************************************************
class ConfigType(Enum):
    DATA = "data"
    SCHEMA = "schema"
    OTHER = "other"

read_type = TypeVar('read_type', covariant=True)
contra_type = TypeVar('contra_type', contravariant=True)
write_type = TypeVar('write_type')
# *****************************************************************************

@runtime_checkable
# *****************************************************************************
class IConfiguration(Protocol, Generic[write_type]):
    # *****************************************************************************
    """
    Abstract base class for managing configurations in a DAQ system.
    """
    _configuration: Optional[write_type] = None
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

    def close_configuration(
        self, partial_close: str, file_names: List[str] | str
    ) -> None:
        """
        Close the current configuration.
        """
        ...

    @property
    def configuration(self) -> Optional[write_type]:
        """
        Get the current configuration.
        :return: The current configuration object.
        """
        return self._configuration

    @configuration.setter
    def configuration(self, value: Optional[write_type]) -> None:
        """
        Set the current configuration.
        :param value: The configuration object to set.
        """
        self._configuration = value

    @property
    def name(self) -> Optional[str]:
        """
        Get the name of the current configuration.
        :return: The name of the current configuration.
        """
        return self._configuration_name

@runtime_checkable
# *****************************************************************************
class _IObjectManager(Protocol, Generic[write_type]):
    # *****************************************************************************
    """
    Abstract base class for managing objects in a configuration.
    """

    def get_obj(*args, **kwargs) -> write_type:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        ...

    def get_all_obj(
        self, object_class: Optional[str | List[str]] = None
    ) -> List[write_type]:
        """
        Get all objects in the current configuration.
        :param object_class: Optional class filter for the objects to retrieve.
        :return: A list of all objects or filtered objects.
        """
        ...


@runtime_checkable
# *****************************************************************************
class INamedObjectManager(_IObjectManager[write_type], Protocol, Generic[write_type]):
    # *****************************************************************************
    """
    Abstract base class for managing objects in a configuration.
    """

    def get_obj(self, object_class: Any, object_name: str) -> write_type:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        ...


@runtime_checkable
# *****************************************************************************
class IClassObjectManager(_IObjectManager[write_type], Protocol, Generic[write_type]):
    # *****************************************************************************
    """
    Abstract base class for managing objects in a configuration.
    """

    def get_obj(self, object_class: Any) -> write_type:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        ...


@runtime_checkable
# *****************************************************************************
class IObjectModifier(Protocol, Generic[read_type]):
    # *****************************************************************************
    _instance: read_type
    
    def set_attr(self, attribute_name: str, attribute_value: Any) -> None:
        """
        Set the value of an attribute of an object in the configuration.
        :param class_name: Class of the object to modify.
        :param attribute_name: Name of the attribute to modify.
        :param attribute_type: Type of the attribute to modify.
        :param kwargs: Additional parameters for the modification.
        """
        ...

    def get_attr(self, attribute_name: str) -> read_type:
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
class _IObjectLifecycle(Protocol, Generic[write_type]):
    # *****************************************************************************
    """
    Abstract base class for add/renaming/deleting objects in a configuration.
    """

    def add(self, obj: write_type) -> None:
        """
        Add an object to the current configuration.
        :param object: The object to add to the configuration.
        """
        ...

    def delete(self, obj: write_type) -> None:
        """
        Remove an object from the configuration.
        :param object_class: Class of the object to remove.
        :param object_name: Name of the object to remove.
        """
        ...

    def rename(self, obj: write_type, new_name: str) -> None:
        """
        Add an object to the current configuration by name.
        :param class_name: Class
        of the object to add.
        :param object_name: Name of the object to add.
        :param attributes: Attributes of the object to add.
        """
        ...

    def create(self, *args, **kwargs)->write_type:
        '''
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param object_name: Name of the object to create.
        '''
        ...


@runtime_checkable
# *****************************************************************************
class INamedObjectLifecycle(_IObjectLifecycle[write_type], Protocol, Generic[write_type]):
    # *****************************************************************************
    def create(
        self, object_class: str, object_name: "str", attributes: Dict[str, Any]
    ) -> write_type:
        """
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param object_name: Arguments for the object creation.
        :param kwargs: Additional parameters for the object creation.
        """
        ...


@runtime_checkable
# *****************************************************************************
class IClassObjectLifecycle(_IObjectLifecycle[write_type], Protocol, Generic[write_type]):
    # *****************************************************************************
    def create(self, object_class: str, attributes: Dict[str, Any]) -> write_type:
        """
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param object_name: Arguments for the object creation.
        :param attributes: Attributes for the object creation.
        """
        ...


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
        self._configuration = configuration

    @property
    def configuration(self) -> Optional[IConfiguration]:
        """
        Get the current configuration.
        :return: The current configuration object.
        """
        return self._configuration

    @configuration.setter
    def configuration(self, value: Optional[IConfiguration]) -> None:
        """
        Set the current configuration.
        :param value: The configuration object to set.
        """
        self._configuration = value

    @property
    def config_type(self) -> ConfigType:
        """
        Get the type of the configuration.
        :return: The type of the configuration (data or schema).
        """
        return self._config_type


