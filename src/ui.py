#!/usr/bin env python3
from xdg import IconTheme

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case
from __feature__ import true_property

import desktopentryparse


class MainWindow(QtWidgets.QMainWindow):
    """App window instance."""
    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        # Main container
        self.main_container = QtWidgets.QWidget()
        self.main_container.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        self.main_container.spacing = 0
        self.set_central_widget(self.main_container)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        self.layout_container.spacing = 0
        self.main_container.set_layout(self.layout_container)

        # App launcher
        self.app_launcher_layout = QtWidgets.QVBoxLayout()
        self.app_launcher_layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        self.app_launcher_layout.spacing = 0
        self.app_launcher_layout.alignment = QtCore.Qt.AlignCenter
        self.layout_container.add_layout(self.app_launcher_layout)

        self.app_launcher = AppLauncher(
            desktopentryparse.DesktopFile(
                '/usr/share/applications/firefox.desktop'))
        self.app_launcher_layout.add_widget(self.app_launcher)


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget."""
    def __init__(self, desktop_file, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        # Main container
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        self.layout_container.spacing = 0
        self.set_layout(self.layout_container)

        # Icon
        self.icon_layout = QtWidgets.QVBoxLayout()
        self.icon_layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        self.icon_layout.spacing = 0
        self.icon_layout.alignment = QtCore.Qt.AlignCenter
        self.layout_container.add_layout(self.icon_layout)

        self.icon_path = IconTheme.getIconPath(
            iconname=desktop_file.as_dict['[Desktop Entry]']['Icon'],
            size=48,
            theme='breeze',
            extensions=['png', 'svg', 'xpm'])

        self.pixmap = QtGui.QPixmap(self.icon_path)
        self.scaled_pixmap = self.pixmap.scaled(
            48, 48, QtCore.Qt.KeepAspectRatio)

        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.stylesheet = (
            'background-color: transparent; padding-top: 10;')
        self.icon_label.pixmap = self.scaled_pixmap
        self.icon_label.alignment = QtCore.Qt.AlignCenter
        self.icon_layout.add_widget(self.icon_label)
