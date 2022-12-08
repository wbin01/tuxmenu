#!/usr/bin env python3
from PySide6 import QtCore, QtWidgets
from __feature__ import snake_case

from widgets.applauncher import AppLauncher
from attachments.desktopentryparse import DesktopFile


class MainWindow(QtWidgets.QMainWindow):
    """App window instance."""
    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        # Main container
        self.main_container = QtWidgets.QWidget()
        self.main_container.set_contents_margins(0, 0, 0, 0)
        self.set_central_widget(self.main_container)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_spacing(0)
        self.main_container.set_layout(self.layout_container)

        # App launcher
        self.app_launcher_layout = QtWidgets.QVBoxLayout()
        self.app_launcher_layout.set_spacing(0)
        self.app_launcher_layout.set_alignment(QtCore.Qt.AlignCenter)
        self.layout_container.add_layout(self.app_launcher_layout)

        self.app_launcher = AppLauncher(
            DesktopFile(
                '/usr/share/applications/firefox.desktop'))
        self.app_launcher_layout.add_widget(self.app_launcher)
