from typing import Optional, Protocol, runtime_checkable, List, Any, Callable
from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import IConfigBackend
import logging
import warnings
from rich.tree import Tree
import networkx as nx
from matplotlib import pyplot as plt

class NotABranchError(Exception):
    """
    Exception raised when an operation is attempted on an object that is not a valid branch.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        
class BranchExistsWarning(UserWarning):
    """
    Exception raised when trying to add a branch that already exists in the tree.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        
class BranchNotFoundWarning(UserWarning):
    """
    Exception raised when a branch is not found in the tree.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigTreeBranch:
    """
    Protocol for a tree branch in the configuration tree.
    Represents a node in the tree structure that can contain data and child branches.
    """
    
    def __init__(self, name: str, id: str, stored_data: Any = None) -> None:
        """
        Initialize a new branch with a name, optional stored data, and a unique identifier.
        Args:
            name: The name of the branch.
            stored_data: Optional data to store in this branch.
            id: Unique identifier for the branch.
        """
        self.name: str = name
        self._stored_data: Any = stored_data
        self.id: str = id
        self._children: List[ConfigTreeBranch] = []  # Type: List[ConfigTreeBranch]
        self._parents: List[ConfigTreeBranch] = []  # Type: List[ConfigTreeBranch]

    @property
    def stored_data(self) -> Any:
        """
        Get the stored data in this branch.
        Returns:
            The stored data (can be None).
        """
        return self._stored_data

    def add_child(self, child: 'ConfigTreeBranch') -> None:
        """
        Add a child branch to this branch.
        Args:
            child: The child branch to add.
        Raises:
            ValueError: If child already exists or is invalid.
        """
        if not isinstance(child, ConfigTreeBranch):
            raise NotABranchError("Child must be an instance of ConfigTreeBranch")
        if child in self._children:
            return
        self._children.append(child)
        child._add_parent(self)

    def _add_child(self, child: 'ConfigTreeBranch') -> None:
        """
        Internal method to add a child branch without checking for duplicates.
        Args:
            child: The child branch to add.
        """
        if not isinstance(child, ConfigTreeBranch):
            raise NotABranchError("Child must be an instance of ConfigTreeBranch")
        
        if child in self._children:
            return
        
        
        self._children.append(child)

    def remove_child(self, child: 'ConfigTreeBranch') -> None:
        """
        Remove a child branch from this branch.
        Args:
            child: The child branch to remove.
        Returns:
            True if child was found and removed, False otherwise.
        """
        if not isinstance(child, ConfigTreeBranch):
            raise ValueError("Child must be an instance of ConfigTreeBranch")
        if child not in self._children:
            logging.debug(f"Child doesn't exist in this branch {self.name}:{self.id}")
        self._children.remove(child)
        child._remove_parent(self)
        
    def _remove_child(self, child: 'ConfigTreeBranch') -> None:
        """
        Internal method to remove a child branch without checking for existence.
        Args:
            child: The child branch to remove.
        """
        if not isinstance(child, ConfigTreeBranch):
            raise NotABranchError("Child must be an instance of ConfigTreeBranch")
        self._children.remove(child)

    def get_children(self) -> List['ConfigTreeBranch']:
        """
        Get an immutable view of child branches.
        Returns:
            List of child branches (should not be modified directly).
        """
        return self._children.copy()
        
    def add_parent(self, parent: 'ConfigTreeBranch') -> None:
        """Get the parent branch of this branch."""
        if not isinstance(parent, ConfigTreeBranch):
            raise NotABranchError("Parent must be an instance of ConfigTreeBranch")
        if parent in self._parents:
            return
        parent.add_child(self)
        self._parents.append(parent)
        
    def _add_parent(self, parent: 'ConfigTreeBranch') -> None:
        """
        Internal method to set the parent branch for this branch without checking for duplicates.
        Note: This should typically only be called by parent's add_child/remove_child.
        """
        if not isinstance(parent, ConfigTreeBranch):
            raise NotABranchError("Parent must be an instance of ConfigTreeBranch")
        if parent in self._parents:
            return    
    
        self._parents.append(parent)
        parent._add_child(self)
    
    def remove_parent(self, parent: 'ConfigTreeBranch') -> None:
        """
        Set the parent branch for this branch.
        Note: This should typically only be called by parent's add_child/remove_child.
        """
        if not isinstance(parent, ConfigTreeBranch):
            raise NotABranchError("Parent must be an instance of ConfigTreeBranch")
        if parent not in self._parents:
            logging.debug(f"Parent doesn't exist in this branch {self.name}:{self.id}")
        self._parents.remove(parent)
        parent.remove_child(self)
        
    def _remove_parent(self, parent: 'ConfigTreeBranch') -> None:
        """
        Internal method to remove a parent branch without checking for existence.
        Note: This should typically only be called by parent's add_child/remove_child.
        """
        if not isinstance(parent, ConfigTreeBranch):
            raise NotABranchError("Parent must be an instance of ConfigTreeBranch")
        self._parents.remove(parent)
        parent._remove_child(self)
        
    def get_parents(self) -> List['ConfigTreeBranch']:
        """
        Get an immutable view of parent branches.
        Returns:
            List of parent branches (should not be modified directly).
        """
        return self._parents.copy()
        
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ConfigTreeBranch):
            return False
        return self.id == value.id and self.name == value.name

class ConfigTree:
    """
    Configuration tree structure.
    Manages the root and provides tree-level operations.
    """
    _backend: IConfigBackend
    _root_branch: Optional[ConfigTreeBranch]
    _branches: List[ConfigTreeBranch]  # All branches in the tree for easy access
    
    def __init__(self, backend: IConfigBackend, root_branch: ConfigTreeBranch) -> None:
        """
        Initialize the configuration tree with a backend.
        Args:
            backend: The configuration backend to use for data storage and retrieval.
        """
        self._backend = backend
        self._root_branch = root_branch  # Type: Optional[ConfigTreeBranch]
        self._branches = [root_branch]  # Type: List[ConfigTreeBranch]
    
    def get_root(self) -> Optional[ConfigTreeBranch]:
        """Get the root branch of the tree (never None)."""
        return self._root_branch
    
    def add_branch(self, parent: Optional[ConfigTreeBranch], branch: ConfigTreeBranch) -> None:
        """
        Add a branch to the tree under specified parent.
        Args:
            parent: None to add as root (replacing current root if exists)
            branch: The branch to add
        """
        if not isinstance(branch, ConfigTreeBranch):
            raise NotABranchError("Branch must be an instance of ConfigTreeBranch")
        
        if parent is None:
            # If no parent specified, set as root branch
            if self._root_branch is not None:
                warnings.warn(
                    "Replacing existing root branch with new one. This will reset the tree!",
                    BranchExistsWarning
                )
            self._root_branch = branch
            self._branches = []
        else:
            branch.add_parent(parent)  # Set parent-child relationship
        
        if self.get_branch_by_name_id(branch.name, branch.id):
            return
        
        self._branches.append(branch)
    
    def remove_branch(self, branch: ConfigTreeBranch) -> None:
        """
        Remove a branch and all its children from the tree.
        Returns:
            True if branch was found and removed, False otherwise.
        """
        if not isinstance(branch, ConfigTreeBranch):
            raise NotABranchError("Branch must be an instance of ConfigTreeBranch")
        if branch not in self._branches:
            logging.debug(f"Branch doesn't exist in the tree: {branch.name}:{branch.id}")
        
        self._branches.remove(branch)
        
    def find_branches(self, predicate: Callable[[ConfigTreeBranch], bool]) -> List[ConfigTreeBranch]:
        """
        Find first branch matching the predicate.
        Args:
            predicate: Function that takes a branch and returns True if it matches
        """
        return [branch for branch in self._branches if predicate(branch)]
        
    def get_branches_by_id(self, branch_id: str) -> List[ConfigTreeBranch]:
        """Get branches with unique identifier.
        :param branch_id: Unique identifier of the branch to find.
        :return: The branch with the specified ID, or empty list if not found.
        """
        predicate = lambda branch: branch.id == branch_id
        return self.find_branches(predicate)        

    def get_branches_by_name(self, name: str) -> List[ConfigTreeBranch]:
        """Get branches with matching name (names may not be unique)."""
        predicate = lambda branch: branch.name == name
        return self.find_branches(predicate)
    
    def get_branches_by_obj(self, obj: Any) -> List[ConfigTreeBranch]:
        """Get branches that contain the specified object.
        :param obj: The object to find in branches.
        :return: List of branches containing the specified object.
        """
        predicate = lambda branch: branch.stored_data == obj
        return self.find_branches(predicate)
    
    def get_branch_by_name_id(self, name: str, branch_id: str) -> Optional[ConfigTreeBranch]:
        """Get branch with matching name and unique identifier. or none
        :param name: Name of the branch to find.
        :param branch_id: Unique identifier of the branch to find.
        
        :return: The branch with the specified name and ID, or None if not found.
        """
        predicate = lambda branch: branch.name == name and branch.id == branch_id
        branches = self.find_branches(predicate)
        if len(branches) > 1:
            logging.warning(f"Multiple branches found with name '{name}' and ID '{branch_id}'. Returning first one.")
        if branches:
            # Only expect one branch with unique ID
            return branches[0]
        
        return None
        
    def get_all_branches(self) -> List[ConfigTreeBranch]:
        """Get all branches in the tree."""
        return self._branches.copy()
    
class TreePrinter:
    """
    Convert the configuration tree to a dictionary representation.
    Args:
        tree: The configuration tree to convert.
    Returns:
        Dictionary representation of the tree.
    """
    def __init__(self, conf_tree: ConfigTree) -> None:
        """
        Initialize the TreePrinter with a configuration tree.
        
        Args:
            conf_tree: The configuration tree to print.
        """
        self._conf_tree = conf_tree
    
    def branch_to_dict(self, branch: ConfigTreeBranch) -> dict:
        return {
            "name": branch.name,
            "id": branch.id,
            "stored_data": branch.stored_data,
            "children": [self.branch_to_dict(child) for child in branch.get_children()],
            "parents": [parent.id for parent in branch.get_parents()]
        }
    
    def tree_to_dict(self) -> dict:
        """
        Convert the entire configuration tree to a nested dictionary.

        Args:
            tree: The configuration tree to convert.
        Returns:
            Dictionary representation of the tree.
        """
        if self._conf_tree.get_root() is None:
            return {}
        
        return {
            "root": self.branch_to_dict(self._conf_tree.get_root()),
            "branches": [self.branch_to_dict(branch) for branch in self._conf_tree.get_all_branches()]
        }
        
    def rich_tree(self, conf_tree: ConfigTree) -> Tree:
        """
        Print the configuration tree in a human-readable format.
        
        Args:
            tree: The configuration tree to print.
        """
        if self._conf_tree.get_root() is None:
            print("The configuration tree is empty.")
            return Tree("Empty Tree")
        
        rich_tree = Tree(f"Schema Tree")
        self._add_branch_to_rich_tree(self._conf_tree.get_root(), rich_tree)
            
        return rich_tree
        
    def _add_branch_to_rich_tree(self, branch: ConfigTreeBranch, parent_node: Tree) -> None:
        """
        Recursively add branches to the rich tree.
        
        Args:
            branch: The branch to add.
            parent_node: The parent node in the rich tree.
        """
        node = parent_node.add(f"{branch.name} ({branch.id})")
        for child in branch.get_children():
            self._add_branch_to_rich_tree(child, node)
            
    def networkx_graph(self) -> nx.DiGraph:
        """
        Convert the configuration tree to a NetworkX directed graph.
        
        Args:
            conf_tree: The configuration tree to convert.
        Returns:
            A NetworkX directed graph representing the tree structure.
        """
        graph = nx.DiGraph()
        for branch in self._conf_tree.get_all_branches():
            graph.add_node(branch.name, stored_data=branch.stored_data)
        
        for branch in self._conf_tree.get_all_branches():
            for child in branch.get_children():
                graph.add_edge(branch.name, child.name)
                
        return graph
    
    def draw_networkx_graph(self, file_name: str = "my_graph.png") -> None:
        """
        Draw the configuration tree as a graph using NetworkX and Matplotlib.
        
        Args:
            conf_tree: The configuration tree to draw.
            file_name: The name of the file to save the graph image.
        """
        graph = self.networkx_graph()
        
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        nx.draw_spring(
            graph,
            with_labels=True,
            node_size=1000,
            node_color='skyblue',
            font_size=8,
            font_color='black',
            font_weight='bold',
            ax=ax,
        )
        fig.savefig(file_name)
