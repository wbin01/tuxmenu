#!/usr/bin/env python3
import sys

from BlurWindow.blurWindow import GlobalBlur
from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case
from __feature__ import true_property

import ui


class TuxMenu(object):
    """..."""
    def __init__(self):
        """..."""
        self.__app_window = QtWidgets.QApplication(sys.argv)
        self.__app_icon = 'tuxmenu.png'
        self.__app_id = 'tuxmenu'
        self.__app_name = 'TuxMenu'
        self.__app_ui = ui.MainWindow()

    @property
    def app_window(self):
        return self.__app_window

    @property
    def app_icon(self):
        return self.__app_icon

    @property
    def app_id(self):
        return self.__app_id

    @property
    def app_name(self):
        return self.__app_name

    @property
    def app_ui(self):
        return self.__app_ui

    def on_quit(self):
        self.app_window.quit()

    def main(self) -> None:
        """..."""
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
        sys.exit(self.app_window.exec())
