from expert_config_ui.daq_config.configuration.implementations.oks.oks_backend import OksKernelBackend
from expert_config_ui.daq_config.configuration.interfaces.tree_interface import ConfigTree, ConfigTreeBranch
from expert_config_ui.daq_config.configuration.implementations.oks.oks_class import OksClassWrapper

class OksSchemaTree(ConfigTree):
    """
    A class to represent a configuration tree based on the OksKernelBackend.
    This class extends ConfigTree to provide a specific implementation for Oks.
    """

    def __init__(self, oks_backend: OksKernelBackend, lowest_level_class: OksClassWrapper):
        """
        Initialize the OksSchemaTree with the given schema file.
        
        :param schema_file: Path to the schema file.
        """
        
        root_branch = ConfigTreeBranch(str(lowest_level_class.get_attr("name")), "root", lowest_level_class)
        super().__init__(oks_backend, root_branch)
        self.generate_branches(root_branch)
    
    def generate_branches(self, parent_branch: ConfigTreeBranch) -> None:
        """
        Generate branches for the configuration tree based on the provided OksClassWrapper.
        
        :param oks_class: The OksClassWrapper instance to generate branches from.
        :return: A list of ConfigTreeBranch instances.
        """

        oks_class = parent_branch.stored_data
        
        for rel in oks_class.get_attr('all_super_classes')():
            wrapped_obj = OksClassWrapper(rel)
            
            branch = ConfigTreeBranch(
                str(wrapped_obj.get_attr("name")),
                wrapped_obj.get_attr("name"),
                wrapped_obj
            )
            
            self.add_branch(parent_branch, branch)
            self.generate_branches(branch)