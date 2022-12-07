#!/usr/bin/env python3
import sys

from BlurWindow.blurWindow import GlobalBlur
from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case
from __feature__ import true_property

import ui


class TuxMenu(object):
    """Desktop menu for Linux written in Python and Qt."""
    def __init__(self):
        """Class constructor."""
        self.__app_window = QtWidgets.QApplication(sys.argv)
        self.__app_icon = 'tuxmenu.png'
        self.__app_name = 'TuxMenu'
        self.__app_ui = ui.MainWindow()

    @property
    def app(self) -> QtWidgets.QApplication:
        """App instance (QApplication)."""
        return self.__app_window

    @property
    def app_icon(self) -> str:
        """App icon path."""
        return self.__app_icon

    @property
    def app_name(self) -> str:
        """App name."""
        return self.__app_name

    @property
    def app_ui(self) -> QtWidgets.QMainWindow:
        """App window instance."""
        return self.__app_ui

    def on_quit(self) -> None:
        """Close the app."""
        self.app.quit()

    def main(self) -> None:
        """Start the app."""
        # Name
        self.app_ui.window_title = self.app_name

        # Icon
        app_icon = QtGui.QIcon(QtGui.QPixmap(self.app_icon))
        self.app_ui.window_icon = app_icon

        # Size
        self.app_ui.minimum_height = 600  # .size = QtCore.QSize(300, 500)
        self.app_ui.minimum_width = 1000  # .show_maximized()

        # Blur
        self.app_ui.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        GlobalBlur(self.app_ui.win_id(), Dark=True, QWidget=self)

        # Show
        self.app_ui.show()
        sys.exit(self.app.exec())
