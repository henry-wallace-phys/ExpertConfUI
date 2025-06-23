from textual.app import App
import click

from expert_config_ui.textual.screens.main_screen import MainScreen
from expert_config_ui.daq_config.configuration.implementations.oks.oks_backend import OksKernelBackend
from expert_config_ui.daq_config.configuration.implementations.conffwk.conffwk_backend import ConffwkBackend

class ExpertConfApp(App):
    """
    Schema Editor Application for the Expert Configuration UI.
    This application provides a user interface for editing schemas in the DAQ system.
    """
    def __init__(self, schema_file: str, **kwargs):
        super().__init__(**kwargs)
        self.title = "Expert Configuration UI - Schema Editor"
        # self._backend = OksKernelBackend()
        self._backend = ConffwkBackend()
        self._backend.open(schema_file)

    def on_mount(self) -> None:
        self.push_screen(MainScreen(self._backend))
        
@click.command()
@click.argument('oks_file')
def main(oks_file: str) -> None:
    """
    Main entry point for the Schema Editor application.
    :param schema_file: Path to the schema file to be edited.
    """
    app = ExpertConfApp(oks_file)
    app.run()
    