from typing import Dict, Any
import oks
import logging
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (IObjectModifier,
                                                                                          INamedObjectLifecycle,
                                                                                          INamedObjectManager)
from expert_config_ui.daq_config.configuration.implementations.oks.oks_kernel import OksKernelInteraction

from enum import Enum

# *****************************************************************************
class OksClassProperties(Enum):
# *****************************************************************************
    '''
    OksClassProperties : Enum for managing properties of classes in the OKS framework.
    This enum defines the properties that can be managed in an OKS class.
    '''
    ATTRIBUTE = "attribute"
    METHOD = "method"
    RELATIONSHIP = "relationship"



# *****************************************************************************
class __OksKernelClassPropManager(INamedObjectManager, OksKernelInteraction):
# *****************************************************************************
    def __init__(self, property_type: OksClassProperties):
        self._property_type = property_type

    def get(self, obj: oks.OksClass, attr_name: str) -> Any:
        '''
        Get the value of an attribute for a specific object in the current configuration.
        :param obj: The object to retrieve the attribute from.
        :param attr_name: Name of the attribute to retrieve.
        :return: Value of the specified attribute.
        '''
        return getattr(obj, f"get_{self._property_type.value}")(attr_name) if hasattr(obj, f"get_{self._property_type.value}") else None

    def get_all(self, obj: oks.OksClass) -> list[Any]:
        '''
        Get all attributes of a specific type for a given object.
        :param obj: The object to retrieve attributes from.
        :return: List of all attributes of the specified type.
        '''
        return getattr(obj, f"all_{self._property_type.value}")()

# *****************************************************************************
class OksKernelClassAttributeManager(__OksKernelClassPropManager):
# *****************************************************************************
    def __init__(self):
        super().__init__(OksClassProperties.ATTRIBUTE)

# *****************************************************************************
class OksKernelClassRelationshipManager(__OksKernelClassPropManager):
# *****************************************************************************
    def __init__(self):
        super().__init__(OksClassProperties.RELATIONSHIP)

# *****************************************************************************
class OksKernelClassMethodManager(__OksKernelClassPropManager):
# *****************************************************************************
    def __init__(self):
        super().__init__(OksClassProperties.METHOD)

# *****************************************************************************     
class __OksKernelClassPropModifer(IObjectModifier, OksKernelInteraction):
# *****************************************************************************     
    '''
    Base class for modifying properties of classes in the OKS configuration.
    '''
    def __init__(self, property_type: OksClassProperties):
        self._property_type = property_type
        __KNOWN_PROPERTIES__ = ['name', 'description']

    def get(self, obj: oks.OksClass, attr_name: str):
        return getattr(obj, f"get_{self._property_type.value}")(attr_name) if hasattr(obj, f"get_{self._property_type.value}") else None

    def set(self, obj: oks.OksClass, attr_name: str, attr_value: Any) -> None:
        '''
        Set an attribute of a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the attribute to set.
        :param attr_value: Value to set for the attribute.
        '''

        prop = self.get(obj, attr_name)
        if prop is None:
            logging.warning(f"Property '{attr_name}' does not exist in class '{obj.get_name()}'.")
            return None
        
        if not hasattr(prop, f"set_{self._property_type.value}"):
            logging.error(f"Property '{attr_name}' does not support modification in class '{obj.get_name()}'.")
            return None
    
        return getattr(prop, f"set_{self._property_type.value}")(attr_value)


# *****************************************************************************     
class OksKernelClassAttributeModifier(__OksKernelClassPropModifer):
# *****************************************************************************     
    '''
    Class for modifying attributes of classes in the OKS configuration.
    '''
    def __init__(self):
        super().__init__(OksClassProperties.ATTRIBUTE)
        self.__KNOWN_PROPERTIES__ = ['name', 'description', 'type', 'range', 'init_value', 'is_multi_values', 'format']

# *****************************************************************************     
class OksKernelClassRelationshipModifier(__OksKernelClassPropModifer):
# *****************************************************************************     
    '''
    Class for modifying relationships of classes in the OKS configuration.
    '''
    def __init__(self):
        super().__init__(OksClassProperties.RELATIONSHIP)
        self.__KNOWN_PROPERTIES__ = ['name', 'description', 'class_type', 'is_composite',
                                     'low_cardinality_constraint', 'high_cardinality_constraint', 
                                     'is_exclusive', 'is_dependent']


# *****************************************************************************     
class OksKernelClassMethodModifier(__OksKernelClassPropModifer):
# *****************************************************************************     
    '''
    Class for modifying methods of classes in the OKS configuration.
    '''
    def __init__(self):
        super().__init__(OksClassProperties.METHOD)
        self.__KNOWN_PROPERTIES__ = ['name', 'description', 'implementation']
    
    def __set_implementation(self, obj: oks.OksClass, attr_name: str, attr_value: Any) -> None:
        '''
        Set the implementation of a method in the OKS class. Requires annoyingly specific treatment.
        :param obj: The object to modify.
        :param attr_name: Name of the method to set the implementation for.
        :param attr_value: Dictionary containing the implementation details.
        '''
        # For adding
        lanuage = attr_value.get('language', ''):
        prototype = attr_value.get('prototype', '')
        body = attr_value.get('body', '')
        
        # For remmoving
        remove = attr_value.get('remove', False)
        
        prop = self.get(obj, attr_name)
        
        if prop is None:
            logging.warning(f"Method '{attr_name}' does not exist in class '{obj.get_name()}'.")
            return None
        
        if remove:
            prop.remove_implementation(attr_name)
        else:
            prop.add_implementation(lanuage, prototype, body)
        
    def set(self, obj: oks.OksClass, attr_name: str, attr_value: Any) -> None:
        if attr_name == 'implementation':
            self.__set_implementation(obj, attr_name, attr_value)        
        else:
            super().set(obj, attr_name, attr_value)

# *****************************************************************************
class _OksKernelClassPropLifecycle(INamedObjectLifecycle, OksKernelInteraction):
# *****************************************************************************
    '''
    Base class for managing the lifecycle of properties in the OKS configuration.
    '''
    def __init__(self, property_type: OksClassProperties):
        self._property_type = property_type

    def add(self, obj: oks.OksClass, attr_name: str) -> None:
        '''
        Add a property to a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the property to add.
        '''
        obj.add(attr_name)

    def delete(self, obj: oks.OksClass, attr_name: str) -> None:
        '''
        Delete a property from a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the property to delete.
        '''
        obj.remove(attr_name)
    
    def rename(self, obj: oks.OksClass, old_name: str, new_name: str) -> None:
        '''
        Rename a property in a class in the configuration.
        :param obj: The object to modify.
        :param old_name: The current name of the property.
        :param new_name: The new name for the property.
        '''
        getattr(obj, f"get_{self._property_type.value}")(old_name).set_name(new_name)
    
    def create(self, obj: oks.OksClass, attr_name: str, attributes: Dict[str, Any]) -> None:
        '''
        Create a new property in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the property to create.
        :param attributes: Attributes of the property to create.
        '''
        raise NotImplementedError(f"Cannot create property in {self.__class__.__name__}. Please define subclass.")

# *****************************************************************************
class OksKernelClassAttributeLifecycle(_OksKernelClassPropLifecycle):
# *****************************************************************************
    '''
    Class for managing the lifecycle of attributes in the OKS configuration.
    '''
    def __init__(self):
        super().__init__(OksClassProperties.ATTRIBUTE)
    
    def create(self, obj: oks.OksClass, attr_name: str, attributes: Dict[str, Any]) -> None:
        '''
        Create a new attribute in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the attribute to create.
        :param attributes: Attributes of the attribute to create. (currently only name)
        '''
        oks.OksAttribute(attr_name, obj)

# *****************************************************************************
class OksKernelClassRelationshipLifecycle(_OksKernelClassPropLifecycle):
# *****************************************************************************
    '''
    Class for managing the lifecycle of relationships in the OKS configuration.
    '''
    def __init__(self):
        super().__init__(OksClassProperties.RELATIONSHIP)
    
    def create(self, obj: oks.OksClass, attr_name: str, attributes: Dict[str, Any]) -> None:
        '''
        Create a new relationship in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the relationship to create.
        :param attributes: Attributes of the relationship to create. (currently only name)
        '''
        type = attributes.get('type', '')
        low_cc = attributes.get('low_cardinality_constraint', 0)
        high_cc = attributes.get('high_cardinality_constraint', 0)
        is_composite = attributes.get('is_composite', False)
        is_exclusive = attributes.get('is_exclusive', False)
        is_dependent = attributes.get('is_dependent', False)
        description = attributes.get('description', '')
        parent = attributes.get('parent', None)

        oks.OksRelationship(attr_name, type, low_cc, high_cc, is_composite, is_exclusive, is_dependent, description, parent, obj)

# *****************************************************************************
class OksKernelClassMethodLifecycle(_OksKernelClassPropLifecycle):
# *****************************************************************************
    '''
    Class for managing the lifecycle of methods in the OKS configuration.
    '''
    def __init__(self):
        super().__init__(OksClassProperties.METHOD)
    
    def create(self, obj: oks.OksClass, attr_name: str, attributes: Dict[str, Any]) -> None:
        '''
        Create a new method in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the method to create.
        :param attributes: Attributes of the method to create. (currently only name)
        '''
        oks.OksMethod(attr_name, obj)