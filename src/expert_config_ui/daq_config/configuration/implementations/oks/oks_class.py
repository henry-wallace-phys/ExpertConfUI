from typing import Any, Dict, List, TypedDict
import oks
from expert_config_ui.daq_config.configuration.implementations.oks.oks_kernel import (
    OksKernelInteraction,
)
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (
    IClassObjectLifecycle,
    IClassObjectManager,
    IObjectModifier,
)
from expert_config_ui.daq_config.configuration.implementations.oks.oks_class_properties import (
    OksAttributeHandler,
    OksMethodHandler,
    OksRelationshipHandler
)

import logging

class PropertyHandlers(TypedDict):
    attribute: OksAttributeHandler
    method: OksMethodHandler
    relationship: OksRelationshipHandler

from typing import Dict, Any

class OksClassWrapper(IObjectModifier[oks.OksClass]):
    __KNOWN_PROPERTIES__ = ["description", "is_abstract", "file"]

    
    def __init__(self, oks_instance: oks.OksClass):
        self._instance = oks_instance
        self._property_handlers: PropertyHandlers = {
            "attribute": OksAttributeHandler(oks_instance),
            "method": OksMethodHandler(oks_instance),
            "relationship": OksRelationshipHandler(oks_instance)
        }
        
    @property
    def attributes(self) -> OksAttributeHandler:
        return self._property_handlers['attribute']
    
    @property
    def methods(self) -> OksMethodHandler:
        return self._property_handlers['method']
    
    @property
    def relationships(self) -> OksRelationshipHandler:
        return self._property_handlers["relationship"]
    
    @property
    def instance(self) -> oks.OksClass:
        return self._instance
    
    def set_attr(self, attr_name: str, attr_value: Any) -> None:
        """
        Set an attribute of a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the attribute to set.
        :param attr_value: Value to set for the attribute.
        """
        if attr_name not in self.__KNOWN_PROPERTIES__:
            logging.warning(
                f"Attribute '{attr_name}' is not a known property of OksClass."
            )

        if hasattr(self.instance, f"set_{attr_name}"):
            getattr(self.instance, f"set_{attr_name}")(attr_value)
        else:
            logging.error(
                f"Attribute '{attr_name}' does not exist in class '{self.get_attr('id')}'."
            )

    def get_attr(self, attr_name: str) -> Any:
        """
        Get an attribute of a class in the configuration.
        :param obj: The object to query.
        :param attr_name: Name of the attribute to get.
        :return: Value of the attribute.
        """
        if attr_name not in self.__KNOWN_PROPERTIES__:
            logging.warning(
                f"Attribute '{attr_name}' is not a known property of OksClass."
            )

        if hasattr(self._, f"get_{attr_name}"):
            return getattr(self._instance, f"get_{attr_name}")()
        else:
            logging.error(
                f"Attribute '{attr_name}' does not exist in class '{self._instance.get_name()}'."
            )
            return None



# *****************************************************************************
class OksKernelClassHandler(
    IClassObjectManager[OksClassWrapper], IClassObjectLifecycle[OksClassWrapper], OksKernelInteraction
):
    # ******************************************************************************

    def get_obj(self, object_class: str) -> OksClassWrapper:
        cls_ = self._configuration.configuration.find_class(object_class)
        
        if cls_ is None:
            logging.error(f"Class '{object_class}' not found in the configuration.")
            raise ValueError(f"Class '{object_class}' not found in the configuration.")
        return OksClassWrapper(cls_)

    def get_all_obj(
        self, object_class: str | list[str] | None = None
    ) -> List[OksClassWrapper]:
        """
        Get all objects in the current configuration.
        If object_class is None, returns all objects in the configuration.
        :param object_class: Class of the objects to retrieve.
        :return: List of all objects in the configuration.
        """
        if object_class is None:
            return [OksClassWrapper(c) for c in self._configuration.configuration.classes()]

        if isinstance(object_class, str):
            object_class = [object_class]

        return [self.get_obj(c) for c in object_class]

    def __copy_class(self, obj: OksClassWrapper, name: str) -> OksClassWrapper:
        cls_ = oks.OksClass(
            name,
            obj.get_description(),
            obj.get_is_abstract(),
            self._configuration.configuration,
        )

        for attr in obj.get_attributes():
            cls_.add_attribute(attr)
        for method in obj.get_methods():
            cls_.add_method(method)
        for rel in obj.get_relationships():
            cls_.add_relationship(rel)
        for sup in obj.get_superclasses():
            cls_.add_superclass(sup)
            
        return OksClassWrapper(cls_)

    def add(self, obj: OksClassWrapper) -> None:
        """
        Add an object to the configuration. [effectively a copy constructor]

        :param obj: The object to add.
        """
        self.__copy_class(obj, obj.get_attr("id"))

    def delete(self, obj: OksClassWrapper) -> None:
        """
        Delete an object from the configuration.
        :param obj: The object to delete.
        """
        oks.OksClass.destroy(obj.instance)

    def rename(self, obj: OksClassWrapper, new_name: str) -> None:
        """
        Rename an object in the configuration.
        :param obj: The object to rename.
        :param new_name: The new name for the object.
        """
        self.__copy_class(obj, new_name)
        self.delete(obj)

    def create(self, object_class: str, attributes: Dict[str, Any]) -> OksClassWrapper:
        """
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param attributes: Attributes of the object to create.
        """

        # Attributes are expected to be of form
        description = attributes.get("description", "")
        is_abstract = attributes.get("is_abstract", False)
        transient = attributes.get("transient", False)

        return OksClassWrapper(
            oks.OksClass(
                object_class,
                description,
                is_abstract,
                self._configuration.configuration,
                transient,
            )
        )
    