from typing import List
import oks
import logging
from expert_config_ui.daq_config.configuration.interfaces.configuration_interface import (
    IConfiguration,
    ConfigurationInteractionBase,
    ConfigType,
)


# *****************************************************************************
class OksKernelConfiguration(IConfiguration):
    # *****************************************************************************
    """
    OksConfiguration : Class for managing configurations using the OKS framework.
    This class implements the IConfiguration interface to provide specific implementations for OKS.

    For now we will only support SCHEMA configurations.
    """
    __CONFIG_NAME_EXTENSION = ".xml"
    __CONFIG_TYPE = ConfigType.SCHEMA

    def __init__(self):
        super().__init__()
        # Use the OKS Kernel to manage configurations
        self._configuration = oks.OksKernel()

    def open_configuration(self, config_name: str) -> None:
        logging.info(config_name)
        
        if not str(config_name).endswith(
            f"{self.__CONFIG_TYPE.name.lower()}{self.__CONFIG_NAME_EXTENSION}"
        ):
            logging.exception(
                f"Configuration name must end with '{self.__CONFIG_TYPE.name.lower()}{self.__CONFIG_NAME_EXTENSION}'"
            )

        logging.info(f"Opening configuration: {config_name}")
        self._configuration.load_schema(config_name)

    def close_configuration(
        self, partial_close: str, file_names: List[str] | str
    ) -> None:
        if not partial_close:
            self._configuration.close_all_schema()
            self._configuration.close_all_data()
        else:
            if isinstance(file_names, str):
                file_names = [file_names]
            for file_name in file_names:
                self._configuration.close_schema(file_name)
                self._configuration.close_data(file_name)

    def save_configuration(self, commit_message: str = "") -> None:
        """
        Save the current configuration to a file.
        :param commit_message: Commit message for the save operation.
        """
        if not self._configuration:
            logging.error("Configuration is not loaded.")
            raise ValueError("Configuration is not loaded.")

        logging.info(f"Saving configuration with commit message: {commit_message}")
        self._configuration.save_all_schema(commit_message)
        self._configuration.save_all_data(commit_message)


# *****************************************************************************
class OksKernelInteraction(ConfigurationInteractionBase):
    # *****************************************************************************
    """
    OksInteraction : Base class for managing interactions with configurations in a DAQ system using the OKS framework.
    """

    def __init__(self, configuration: IConfiguration):
        if not isinstance(configuration, OksKernelConfiguration):
            raise TypeError("Configuration must be an instance of OksConfiguration.")
        super().__init__(ConfigType.SCHEMA, configuration)
