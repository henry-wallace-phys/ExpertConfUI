import conffwk
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (
    IConfiguration,
    INamedObjectLifecycle,
    INamedObjectManager,
    ConfigurationInteractionBase,
    IObjectModifier,
    ConfigType,
)
import logging
from typing import Optional, List, Any, Dict, TypeVar



# *****************************************************************************
class ConffwkConfiguration(IConfiguration[conffwk.Configuration]):
    # *****************************************************************************
    __CONFIG_NAME_EXTENSION = ".xml"
    __CONFIG_TYPE = ConfigType.DATA

    def open_configuration(self, configuration_name: str) -> None:
        """
        Open the configuration using the Conffwk framework.
        :param configuration_name: Name of the configuration to open.
        """
        if not str(configuration_name).endswith(
            f"{self.__CONFIG_TYPE.name.lower()}{self.__CONFIG_NAME_EXTENSION}"
        ):
            logging.exception(
                f"Configuration name must end with '{self.__CONFIG_TYPE.name.lower()}{self.__CONFIG_NAME_EXTENSION}'"
            )

        logging.info(f"Opening configuration: {configuration_name}")
        self.configuration_name = configuration_name
        self.configuration = conffwk.Configuration(f"oksconflibs:{configuration_name}")

    def close_configuration(self, partial_close: bool, _: Any = None) -> None:
        """
        Close the current configuration.
        :param partial_close: Optional parameter to specify if the close is partial.
        :param file_names: Optional file names to close.
        """
        if self.configuration is None:
            raise ValueError("Configuration is not loaded.")

        logging.info(f"Closing configuration: {self.configuration_name}")
        if partial_close:
            logging.warning("Partial close is not supported in ConffwkConfiguration.")

        self.configuration.unload()

    def save_configuration(self, commit_message: str = "") -> None:
        """
        Save the current configuration to a file.
        :param commit_message: Commit message for the save operation.
        """
        self.configuration.commit(commit_message)

class ConffwkObjectModifier(IObjectModifier[conffwk.dal.DalBase]):
    def __init__(self, dal_obj: conffwk.dal.DalBase) -> None:
        self._instance = dal_obj
        self.configuration = getattr(dal_obj, "configuration", None)
        
    @property
    def instance(self) -> conffwk.dal.DalBase:
        return self._instance    
    
    def check_is_dal(self, obj: object | List[object]) -> bool:
        '''
        Bit hacky, checks to see if the object is a DAL object. Can't check classes because it's not 
        got pybind but this will do the job.
        :param obj: The object or list of objects to check.
        :return: True if the object is a DAL object, False otherwise.
        '''
        if not isinstance(obj, list):
            obj = [obj]
        
        if any([o.__module__ == "conffwk.dal" for o in obj]):
            return True
        return False

    def set_attr(self, attr_name: str, attr_value: Any) -> None:
        """
        Modify an attribute of an object in the current configuration.
        :param object_class: Class of the object to modify.
        :param object_name: Name of the object to modify.
        :param attr_name: Name of the attribute to modify.
        :param attr_value: New value for the attribute.
        """

        if self.configuration is None:
            raise ValueError("Configuration is not loaded.")
        
        # Make sure we add the attribute to the dal object
        # not our handler!
        if self.check_is_dal(attr_value):
            if isinstance(attr_value, list):
                attr_value = [ConffwkObjectModifier(a) for a in attr_value]
            else:
                attr_value = ConffwkObjectModifier(attr_value)
        
        
        setattr(self._instance, attr_name, attr_value)
        self.configuration.configuration.update_dal(self._instance)


    def get_attr(self, attr_name: str) -> Optional[Any]:
        """
        Get the value of an attribute for a specific object in the current configuration.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :param attr_name: Name of the attribute to retrieve.
        :return: Value of the specified attribute.
        """
        
        attr = getattr(self._instance, attr_name) if hasattr(self._instance, attr_name) else None
        print(attr[0].__module__)
        
        # Do some processing to make sure everything stays wrapped up
        if self.check_is_dal(attr):
            return attr
        elif isinstance(attr, list):
            return [ConffwkObjectModifier(a) for a in attr]
        else: # It's a single dal object
            return ConffwkObjectModifier(attr)
    
    def __str__(self) -> str:
        return f"{self._instance}"

# *****************************************************************************
class ConffwkObjectHandler(
    ConfigurationInteractionBase,
    INamedObjectManager[conffwk.dal.DalBase],
    INamedObjectLifecycle[conffwk.dal.DalBase],
):
    # *****************************************************************************
    def __init__(self, configuration: IConfiguration):
        if not isinstance(configuration, ConffwkConfiguration):
            raise TypeError(
                "Configuration must be an instance of ConffwkConfiguration."
            )
        super().__init__(config_type=ConfigType.DATA, configuration=configuration)

    def get_obj(self, object_class: str, object_name: str)->ConffwkObjectModifier:
        """
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        """
        if self.configuration.configuration is None:
            raise ValueError("Configuration is not loaded.")

        return ConffwkObjectModifier(self.configuration.configuration.get_dal(object_class, object_name))

    def get_all_obj(self, object_class: Optional[str | List[str]] = None)->List[ConffwkObjectModifier]:
        """
        Get all objects in the current configuration.
        :param object_class: Optional class filter for the objects to retrieve.
        :return: A list of all objects or filtered objects.
        """
        if self.configuration.configuration is None:
            raise ValueError("Configuration is not loaded.")

        if isinstance(object_class, str):
            object_class = [object_class]

        if object_class:
            return [ConffwkObjectModifier(d) for c in self.configuration.configuration.get_dals(object_class)for d in c]
        
        return [ConffwkObjectModifier(d) for d in self.configuration.configuration.get_all_dals()]
    

    def delete(self, object: ConffwkObjectModifier) -> None:
        """
        Delete an object from the current configuration.
        :param object: The object to delete.
        """
        self.configuration.configuration.destroy_dal(object.instance)
        self.configuration.configuration.update_dal(object.instance)

    def add(self, object: conffwk.dal.DalBase) -> None:
        """
        Add an object to the current configuration.
        :param object: The object to add to the configuration.
        """
        self.configuration.configuration.add_dal(object.instance)
        self.configuration.configuration.update_dal(object.instance)

    def rename(self, obj: conffwk.dal.DalBase, new_name: str) -> None:
        obj.rename(new_name)
        self.configuration.configuration.update_dal(obj.instance)

    def create(
        self, object_class: str, object_name: str, attributes: Dict[str, Any]
    ) -> conffwk.dal.DalBase:
        """
        Create a new object of the specified class and name.
        :param object_class: Class of the object to create.
        :param object_name: Name of the object to create.

        :attributes: Set attribtue of the object create. These are specific to the object class. Dict should be of form:
        {
            'attribute_name': attribute_value,
        }

        :return: The created object.
        """
        obj = self.configuration.configuration.create_dal(object_class, object_name)
        self.configuration.configuration.update_dal(obj)

        for attr_name, attr_value in attributes.items():
            if hasattr(obj, attr_name):
                self.set_attr(obj, attr_name, attr_value)
            else:
                logging.warning(
                    f"Attribute '{attr_name}' not found in object '{object_class}'."
                )
        self.configuration.configuration.update_dal(obj)
        return ConffwkObjectModifier(obj)