from typing import Any, Dict
import oks
from expert_config_ui.daq_config.configuration.implementations.oks.oks_kernel import (
    OksKernelInteraction,
)
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (
    IClassObjectLifecycle,
    IClassObjectManager,
    IObjectModifier,
)
import logging

# *****************************************************************************
class OksKernelClassHandler(IClassObjectManager, IObjectModifier, IClassObjectLifecycle, OksKernelInteraction):
# ******************************************************************************
    __KNOWN_PROPERTIES__ = ["description", "is_abstract", "file"]

    def get_obj(self, object_class: str) -> oks.OksClass:
        return self._configuration.configuration.find_class(object_class)

    def get_all_obj(
        self, object_class: str | list[str] | None = None
    ) -> list[oks.OksClass]:
        """
        Get all objects in the current configuration.
        If object_class is None, returns all objects in the configuration.
        :param object_class: Class of the objects to retrieve.
        :return: List of all objects in the configuration.
        """
        if object_class is None:
            return self._configuration.configuration.classes()

        if isinstance(object_class, str):
            return [self.get_obj(object_class)]

        return [self.get_obj(c) for c in object_class]

    def set_attr(self, obj: oks.OksClass, attr_name: str, attr_value: Any) -> None:
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

        if hasattr(obj, f"set_{attr_name}"):
            getattr(obj, f"set_{attr_name}")(attr_value)
        else:
            logging.error(
                f"Attribute '{attr_name}' does not exist in class '{obj.get_name()}'."
            )

    def get_attr(self, obj: oks.OksClass, attr_name: str) -> Any:
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

        if hasattr(obj, f"get_{attr_name}"):
            return getattr(obj, f"get_{attr_name}")()
        else:
            logging.error(
                f"Attribute '{attr_name}' does not exist in class '{obj.get_name()}'."
            )
            return None

    def __copy_class__(self, obj: oks.OksClass, name: str) -> oks.OksClass:
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

    def add(self, obj: oks.OksClass) -> None:
        """
        Add an object to the configuration. [effectively a copy constructor]

        :param obj: The object to add.
        """
        self.__copy_class__(obj, obj.get_name())

    def delete(self, obj: oks.OksClass) -> None:
        """
        Delete an object from the configuration.
        :param obj: The object to delete.
        """
        oks.OksClass.destroy(obj)

    def rename(self, obj: oks.OksClass, new_name: str) -> None:
        """
        Rename an object in the configuration.
        :param obj: The object to rename.
        :param new_name: The new name for the object.
        """
        self.__copy_class__(obj, new_name)
        self.delete(obj)

    def create(self, object_class: str, attributes: Dict[str, Any]) -> None:
        """
        Create a new object in the configuration.
        :param object_class: Class of the object to create.
        :param attributes: Attributes of the object to create.
        """

        # Attributes are expected to be of form
        description = attributes.get("description", "")
        is_abstract = attributes.get("is_abstract", False)
        transient = attributes.get("transient", False)

        oks.OksClass(
            object_class,
            description,
            is_abstract,
            self._configuration.configuration,
            transient,
        )
