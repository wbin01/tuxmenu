#!/usr/bin/env python3
import sys

from PySide6 import QtCore, QtWidgets

from __feature__ import snake_case
from __feature__ import true_property

import ui


class TuxMenu(object):
    """..."""
    def __init__(self):
        """..."""
        self.__app = QtWidgets.QApplication([])
        self.__app_id = 'xcellapp'
        self.__app_name = 'TuxMenu'
        self.__app_ui = ui.MainWindow()

    @property
    def app(self):
        return self.__app

    @property
    def app_id(self):
        return self.__app_id

    @property
    def app_name(self):
        return self.__app_name

    @property
    def app_ui(self):
        return self.__app_ui

    def main(self) -> None:
        """..."""
        # Settings
        # self.app_ui.window_title = self.__app_name
        self.app_ui.minimum_height = 600
        self.app_ui.minimum_width = 1000
        # self.app_ui.show_maximized()
        # self.__ui.size = QtCore.QSize(300, 500)

        # Show
        # self.app.application_name = "Audio Sources Example"
        self.app_ui.show()

        sys.exit(self.app.exec())
