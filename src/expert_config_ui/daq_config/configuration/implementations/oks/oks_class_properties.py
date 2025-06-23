from typing import Dict, Any, TypeVar, Generic, List, Optional
import oks
import logging
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (
    IObjectModifier,
    INamedObjectLifecycle,
    INamedObjectManager,
)

from enum import Enum


# *****************************************************************************
class OksClassProperties(Enum):
    # *****************************************************************************
    """
    OksClassProperties : Enum for managing properties of classes in the OKS framework.
    This enum defines the properties that can be managed in an OKS class.
    """
    ATTRIBUTE = "attribute"
    METHOD = "method"
    RELATIONSHIP = "relationship"


T = TypeVar("T")
# *****************************************************************************
class OksClassPropertyModifier(IObjectModifier[T], Generic[T]):
    # *****************************************************************************
    """
    Class for managing the methods in the OKS configuration.
    """

    def __init__(self, oks_object: Optional[T]):
        self._instance: Optional[T] = oks_object

    @property
    def instance(self) -> T | None:
        """
        Get the underlying OKS object.
        :return: The underlying OKS object.
        """
        return self._instance

    def get_attr(self, attr_name: str):
        return (
            getattr(self._instance, f"get_{attr_name}")()
            if hasattr(self._instance, f"get_{attr_name}")
            else None
        )

    def set_attr(self, attr_name: str, attr_value: Any) -> None:
        """
        Set an attribute of a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the attribute to set.
        :param attr_value: Value to set for the attribute.
        """
        
        return (
            getattr(self._instance, f"set_{attr_name}")(attr_value)
            if hasattr(self._instance, f"set_{attr_name}")
            else None
        )

    def __eq__(self, value: object) -> bool:
        if isinstance(value, OksClassPropertyModifier):
            return self._instance == value.instance
        
        return False

# *****************************************************************************
class _OksClassPropertyHandler(INamedObjectLifecycle[oks.OksClass], INamedObjectManager[oks.OksClass], Generic[T]):
# *****************************************************************************
    """Class for managing properties of classes in the OKS configuration.
    """
    def __init__(self, oks_class: oks.OksClass, property_type: OksClassProperties):
        self._oks_class = oks_class
        self._property_type = property_type
        self.__KNOWN_PROPERTIES__ = []
    
    def get_obj(self, attr_name: str) -> OksClassPropertyModifier[T]:
        """
        Get the value of an attribute for a specific object in the current configuration.
        :param obj: The object to retrieve the attribute from.
        :param attr_name: Name of the attribute to retrieve.
        :return: Value of the specified attribute.
        """
        return (
            OksClassPropertyModifier[T](getattr(self._oks_class, f"find_{self._property_type.value}")(attr_name))
            if hasattr(self._oks_class, f"find_{self._property_type.value}")
            else OksClassPropertyModifier(None)
        )

    def get_all_obj(self) -> List[OksClassPropertyModifier[T]]:
        """
        Get all attributes of a specific type for a given object.
        :param obj: The object to retrieve attributes from.
        :return: List of all attributes of the specified type.
        """
        vals =  getattr(self._oks_class, f"all_{self._property_type.value}s")()
        return [OksClassPropertyModifier[T](val) for val in vals] if vals else []

    def add(self, attr: OksClassPropertyModifier[T]) -> None:
        """
        Add a property to a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the property to add.
        """
        self._oks_class.add(attr.instance)

    def delete(self, attr: OksClassPropertyModifier[T]) -> None:
        """
        Delete a property from a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the property to delete.
        """
        self._oks_class.remove(attr)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        Rename a property in a class in the configuration.
        :param obj: The object to modify.
        :param old_name: The current name of the property.
        :param new_name: The new name for the property.
        """
        getattr(self._oks_class, f"get_{self._property_type.value}")(old_name).set_name(new_name)

    def create(
        self, attr_name: str, attributes: Dict[str, Any]
    ) -> OksClassPropertyModifier[T]:
        """
        Create a new property in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the property to create.
        :param attributes: Attributes of the property to create.
        """
        raise NotImplementedError(
            f"Cannot create property in {self.__class__.__name__}. Please define subclass."
        )
        


# *****************************************************************************
class OksAttributeHandler(_OksClassPropertyHandler[oks.OksAttribute]):
    # *****************************************************************************
    """
    Handler for managing attributes in the OKS configuration.
    """

    def __init__(self, oks_class: oks.OksClass):
        super().__init__(oks_class, OksClassProperties.ATTRIBUTE)
        self.__KNOWN_PROPERTIES__ = [
            "name",
            "description",
            "type",
            "range",
            "init_value",
            "is_multi_values",
            "format",
        ]

    def create(
        self, attr_name: str, attributes: Dict[str, Any]
    ) -> OksClassPropertyModifier[oks.OksAttribute]:
        """
        Create a new attribute in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the attribute to create.
        :param attributes: Attributes of the attribute to create. (currently only name)
        """
        return OksClassPropertyModifier(oks.OksAttribute(attr_name, self._oks_class))

# *****************************************************************************
class OksRelationshipHandler(_OksClassPropertyHandler[oks.OksRelationship]):
    # *****************************************************************************
    """
    Handler for managing relationships in the OKS configuration.
    """

    def __init__(self, oks_class: oks.OksClass):
        super().__init__(oks_class, OksClassProperties.ATTRIBUTE)
        self.__KNOWN_PROPERTIES__ = [
            "name",
            "description",
            "type",
            "low_cardinality_constraint",
            "high_cardinality_constraint",
            "is_composite",
            "is_exclusive",
            "is_dependent",
        ]

    def create(
        self, attr_name: str, attributes: Dict[str, Any]
    ) -> OksClassPropertyModifier[oks.OksRelationship]:
        """
        Create a new relationship in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the relationship to create.
        :param attributes: Attributes of the relationship to create. (currently only name)
        """
        type = attributes.get("type", "")
        low_cc = attributes.get("low_cardinality_constraint", 0)
        high_cc = attributes.get("high_cardinality_constraint", 0)
        is_composite = attributes.get("is_composite", False)
        is_exclusive = attributes.get("is_exclusive", False)
        is_dependent = attributes.get("is_dependent", False)
        description = attributes.get("description", "")
        parent = attributes.get("parent", None)

        rel = oks.OksRelationship(
            attr_name,
            type,
            low_cc,
            high_cc,
            is_composite,
            is_exclusive,
            is_dependent,
            description,
            parent,
            self._oks_class,
        )
        return OksClassPropertyModifier(rel)


#******************************************************************************
class OksMethodPropertyHandler(OksClassPropertyModifier[oks.OksMethod]):
    """_summary_
    Specialisation of OksClassPropertyHandler for handling methods in OKS.
    """
    def __init__(self, oks_method: oks.OksMethod):
        """
        Initialize the OksMethodPropertyHandler with an OksMethod instance.
        :param oks_method: The OksMethod instance to handle.
        """
        if not isinstance(oks_method, oks.OksMethod):
            raise TypeError("Expected an instance of oks.OksMethod")
        super().__init__(oks_method)

    def __set_implementation(
        self, attr_name: str, attr_value: Any
    ) -> None:
        """
        Set the implementation of a method in the OKS class. Requires annoyingly specific treatment.
        :param obj: The object to modify.
        :param attr_name: Name of the method to set the implementation for.
        :param attr_value: Dictionary containing the implementation details.
        """
        # For adding
        lanuage = attr_value.get("language", "")
        prototype = attr_value.get("prototype", "")
        body = attr_value.get("body", "")

        # For remmoving
        remove = attr_value.get("remove", False)

        prop = self.get_attr(attr_name)

        if prop is None:
            logging.warning(
                f"Method '{attr_name}' does not exist in class '{self._obj.name()}'."
            )
            return None

        if remove:
            prop.remove_implementation(attr_name)
        else:
            prop.add_implementation(lanuage, prototype, body)

    def set_attr(self, attr_name: str, attr_value: Any) -> None:
        if attr_name == "implementation":
            self.__set_implementation(attr_name, attr_value)
        else:
            super().set_attr(attr_name, attr_value)
    

# *****************************************************************************
class OksMethodHandler(_OksClassPropertyHandler[oks.OksMethod]):
    # *****************************************************************************
    def __init__(self, oks_class: oks.OksClass):
        super().__init__(oks_class, OksClassProperties.METHOD)
        self.__KNOWN_PROPERTIES__ = [
            "name",
            "description",
            "implementation",
        ]

    def create(
        self, attr_name: str, attributes: Dict[str, Any]
    ) -> OksMethodPropertyHandler:
        """
        Create a new method in a class in the configuration.
        :param obj: The object to modify.
        :param attr_name: Name of the method to create.
        :param attributes: Attributes of the method to create. (currently only name)
        """
        m = oks.OksMethod(attr_name, self._oks_class)
        return OksMethodPropertyHandler(m)