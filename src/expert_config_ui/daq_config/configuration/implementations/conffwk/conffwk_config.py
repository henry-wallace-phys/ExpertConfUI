import conffwk
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (IConfiguration,
                                                                                          INamedObjectLifecycle,
                                                                                          INamedObjectManager,
                                                                                          ConfigurationInteractionBase,
                                                                                          ConfigType)
import logging
from typing import Optional, List, Any, Dict

# *****************************************************************************
class ConffwkConfiguration(IConfiguration):
# *****************************************************************************
    __CONFIG_NAME_EXTENSION=".xml"
    __CONFIG_TYPE = ConfigType.DATA
    
    def __init__(self):
        self._configuration = None
        
    def open(self, configuration_name: str) -> None:
        '''
        Open the configuration using the Conffwk framework.
        :param configuration_name: Name of the configuration to open.
        '''
        if not str(configuration_name).endswith(f"{self.__CONFIG_TYPE.name.lower()}{self.__CONFIG_NAME_EXTENSION}"):
            logging.exception(f"Configuration name must end with '{self.__CONFIG_TYPE.name.lower()}{self.__CONFIG_NAME_EXTENSION}'")
        
        logging.info(f"Opening configuration: {configuration_name}")
        self._configuration_name = configuration_name
        self._configuration = conffwk.Configuration(f"oksconflibs:{configuration_name}")
    
    def save_configuration(self, commit_message: str = "") -> None:
        '''
        Save the current configuration to a file.
        :param commit_message: Commit message for the save operation.
        '''        
        self._configuration.commit(commit_message)

# *****************************************************************************
class ConffwkInteraction(ConfigurationInteractionBase):
# *****************************************************************************
    '''
    ConffwkInteraction : Base class for managing interactions with configurations in a DAQ system using the Conffwk framework.
    '''
    def __init__(self, configuration: IConfiguration):
        if not isinstance(configuration, ConffwkConfiguration):
            raise TypeError("Configuration must be an instance of ConffwkConfiguration.")
        super().__init__(ConfigType.DATA, configuration)

class ConffwkObjectManager(INamedObjectManager, ConffwkInteraction):
    def get(self, object_class: str, object_name: str):
        '''
        Get an object of the specified class and name.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :return: The requested object.
        '''
        if self._configuration.configuration is None:
            raise ValueError("Configuration is not loaded.")
        
        return self._configuration.configuration.get_dal(object_class, object_name)
    
    def get_all(self, object_class: Optional[str | List[str]] = None):
        '''
        Get all objects in the current configuration.
        :param object_class: Optional class filter for the objects to retrieve.
        :return: A list of all objects or filtered objects.
        '''
        if self._configuration.configuration is None:
            raise ValueError("Configuration is not loaded.")
        
        if isinstance(object_class, str):
            object_class = [object_class]
        
        return [d for c in self._configuration.configuration.get_dals(object_class) for d in c] if object_class else self._configuration.configuration.get_all_dals()

# *****************************************************************************
class ConffwkObjectModifier(ConffwkObjectManager, INamedObjectManager):    
# *****************************************************************************
    def set(self, obj: conffwk.DalBase, attr_name: str, attr_value: Any) -> None:
        '''
        Modify an attribute of an object in the current configuration.
        :param object_class: Class of the object to modify.
        :param object_name: Name of the object to modify.
        :param attr_name: Name of the attribute to modify.
        :param attr_value: New value for the attribute.
        '''
        if self._configuration.configuration is None:
            raise ValueError("Configuration is not loaded.")
        
        setattr(obj, attr_name, attr_value)
        self._configuration.configuration.update_dal(obj)
    
    def get(self, obj: conffwk.DalBase, attr_name: str)-> Optional[Any]:
        '''
        Get the value of an attribute for a specific object in the current configuration.
        :param object_class: Class of the object to retrieve.
        :param object_name: Name of the object to retrieve.
        :param attr_name: Name of the attribute to retrieve.
        :return: Value of the specified attribute.
        '''        
        return getattr(obj, attr_name) if hasattr(obj, attr_name) else None

# *****************************************************************************
class ConffwkObjectLifecycle(ConffwkObjectManager, INamedObjectLifecycle):
# *****************************************************************************
    '''
    ConffwkObjectLifecycle : Class for managing the lifecycle of objects in a configuration using the Conffwk framework.
    '''
    
    def delete(self, object: conffwk.DalBase) -> None:
        '''
        Delete an object from the current configuration.
        :param object: The object to delete.
        '''        
        self._configuration.configuration.destroy_dal(object)
        self._configuration.configuration.update_dal(object)
        
    def add(self, object: conffwk.DalBase) -> None:
        '''
        Add an object to the current configuration.
        :param object: The object to add to the configuration.
        '''
        self._configuration.configuration.add_dal(object)
        self._configuration.configuration.update_dal(object)
        
    def rename(self, obj: conffwk.DalBase, new_name: str) -> None:
        obj.rename(new_name)
        self._configuration.configuration.update_dal(obj)
        
    def create(self, object_class: str, object_name: str, attributes: Dict[str, Any]) -> None:
        '''
        Create a new object of the specified class and name.
        :param object_class: Class of the object to create.
        :param object_name: Name of the object to create.
        
        :attributes: Set attribtue of the object create. These are specific to the object class. Dict should be of form:
        {
            'attribute_name': attribute_value,
        }
            
        :return: The created object.
        '''
        obj = self._configuration.configuration.create_dal(object_class, object_name)
        self._configuration.configuration.update_dal(obj)
                
        attribute_manager = ConffwkObjectModifier(self._configuration)
        
        for attr_name, attr_value in attributes.items():
            if hasattr(obj, attr_name):
                attribute_manager.set(obj, attr_name, attr_value)
            else:
                logging.warning(f"Attribute '{attr_name}' not found in object '{object_class}'.")
        self._configuration.configuration.update_dal(obj)
        