from textual.screen import Screen

from expert_config_ui.textual.widgets.backend_display import BackendDisplay
from expert_config_ui.daq_config.configuration.interfaces.configuration_backend import IConfigBackend

class MainScreen(Screen):
    """
    Main screen for the Expert Configuration UI.
    Displays the backend handler and allows interaction with it.
    """

    def __init__(self, backend: IConfigBackend, **kwargs):
        super().__init__(**kwargs)
        self.backend: IConfigBackend = backend

    def compose(self):
        yield BackendDisplay(self.backend, id="backend_display")


