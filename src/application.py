#!/usr/bin/env python3
import sys

from BlurWindow.blurWindow import GlobalBlur
from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

import window


class Application(object):
    """Desktop menu for Linux written in Python and Qt."""
    def __init__(self, args):
        """Class constructor."""
        self.application = QtWidgets.QApplication(args)
        self.application_icon = 'tuxmenu.png'
        self.application_name = 'TuxMenu'
        self.application_window = window.MainWindow()

    def on_quit(self) -> None:
        """Close the app."""
        self.app.quit()

    def main(self) -> None:
        """Start the app."""
        # Name
        self.application_window.set_window_title(self.application_name)

        # Icon
        app_icon = QtGui.QIcon(QtGui.QPixmap(self.application_icon))
        self.application_window.set_window_icon(app_icon)

        # Size
        self.application_window.set_minimum_height(600)
        self.application_window.set_minimum_width(1000)

        # Blur
        self.application_window.set_attribute(
            QtCore.Qt.WA_TranslucentBackground)
        GlobalBlur(self.application_window.win_id(), Dark=True, QWidget=self)

        # Show
        self.application_window.show_maximized()  # .show_full_screen() .show()
        sys.exit(self.application.exec())
