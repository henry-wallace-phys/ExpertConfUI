from expert_config_ui.daq_config.configuration.implementations.oks.oks_backend import OksKernelBackend
from expert_config_ui.daq_config.configuration.implementations.conffwk.conffwk_backend import ConffwkBackend
from expert_config_ui.daq_config.data_structures.oks.oks_schema_tree import OksSchemaTree
from expert_config_ui.daq_config.configuration.interfaces.tree_interface import TreePrinter
import rich
import networkx as nx
from matplotlib import pyplot as plt
import logging

def test_schema(schema_file: str, data_file: str) -> None:
    """
    Test function to validate the schema of the configuration interfaces.
    """
    oks_backend = OksKernelBackend(schema_file)
    session_schema_obj = oks_backend.handler.get_obj("Session")

    conffwk_backend = ConffwkBackend(data_file)
    conffwk_backend.open(data_file)
    session_instance = conffwk_backend.handler.get_obj("Session", "np02-session")
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # import sys
    # if len(sys.argv) != 3:
    #     print("Usage: python test_schema.py <schema_file> <database>")
    #     sys.exit(1)

    # SCHEMA = sys.argv[1]
    # DATABASE = sys.argv[2]

    SCHEMA = "schema/appmodel/application.schema.xml"
    DATABASE = "/home/hwallace/scratch/dune_software/daq/daq_work_areas/NFD_DEV_250514_A9/np02-runs/sessions/np02-session.data.xml"

    test_schema(SCHEMA, DATABASE)
    print("Schema test completed successfully.")
