#!/usr/bin env python3
from xdg import IconTheme

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

import desktopentryparse


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
            desktopentryparse.DesktopFile(
                '/usr/share/applications/firefox.desktop'))
        self.app_launcher_layout.add_widget(self.app_launcher)


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget."""
    def __init__(self, desktop_file, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_spacing(0)
        self.set_layout(self.layout_container)

        # Icon
        self.icon_layout = QtWidgets.QVBoxLayout()
        self.icon_layout.set_spacing(0)
        self.icon_layout.set_alignment(QtCore.Qt.AlignCenter)
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
        self.icon_label.set_style_sheet(
            'background-color: transparent; padding-top: 10;')
        self.icon_label.set_pixmap(self.scaled_pixmap)
        self.icon_label.set_alignment(QtCore.Qt.AlignCenter)
        self.icon_layout.add_widget(self.icon_label)
