from textual.widgets import Static, Button
from textual.containers import ScrollableContainer
import logging
from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import IConfigBackend

from typing import List, Any

'''
Set of objects for displaying objects in the backend handler.
'''
class BackendDisplay(Static):
    PLACEHOLDER_STR = "____"
    
    def __init__(self, backend: IConfigBackend, **kwargs):
        super().__init__(**kwargs)
        self.backend: IConfigBackend = backend

        self.refresh()        

    def compose(self):
        with ScrollableContainer(id="backend_display_grid", classes="scrollable_grid"):
            for obj in self.backend.handler.get_all_obj():
                obj_id = obj.name.replace(".", self.PLACEHOLDER_STR)
                
                yield Button(
                    obj.name,
                    id=f"btn_{obj_id}",
                    variant="primary",
                    classes="backend_button",
                )