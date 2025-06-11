from expert_config_ui.daq_config.configuration.implementations.oks.oks_backend import OksKernelBackend
from expert_config_ui.daq_config.configuration.implementations.oks.oks_class_properties import OksKernelAttributeHandler
from expert_config_ui.daq_config.configuration.implementations.conffwk.conffwk_backend import ConffwkBackend

def test_schema(schema_file: str) -> None:
    """
    Test function to validate the schema of the configuration interfaces.
    """
    oks_backend = OksKernelBackend(config_path=None)
    # conffwk_backend_instance = ConffwkBackend(config_path=None)

    oks_backend.open(schema_file)
    fake_hsi = oks_backend.get_handler("class_obj").get_obj("DFOConf")
    rels_handler: OksKernelAttributeHandler = oks_backend.get_handler("attribute")
    
    rels = rels_handler.get_obj(fake_hsi, "general_queue_timeout_ms")
    
    print(rels_handler.get_attr(rels, "name"))
    rels_handler.set_attr(rels, "name", "silly_name")
    print(rels_handler.get_attr(rels, "name"))

    
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_schema.py <schema_file>")
        sys.exit(1)

    SCHEMA = sys.argv[1]

    test_schema(SCHEMA)
    print("Schema test completed successfully.")
