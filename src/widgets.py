#!/usr/bin env python3
from xdg import IconTheme

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget."""
    def __init__(self, desktop_file, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_spacing(0)
        self.set_layout(self.layout_container)

        # Icon
        self.icon_path = IconTheme.getIconPath(
            iconname=desktop_file.as_dict['[Desktop Entry]']['Icon'],
            size=48,
            theme='breeze',
            extensions=['png', 'svg', 'xpm'])

        self.pixmap = QtGui.QPixmap(self.icon_path)
        self.scaled_pixmap = self.pixmap.scaled(
            48, 48, QtCore.Qt.KeepAspectRatio)

        self.icon_view = QtWidgets.QLabel(self)
        self.icon_view.set_pixmap(self.scaled_pixmap)
        self.icon_view.set_alignment(QtCore.Qt.AlignCenter)
        self.layout_container.add_widget(self.icon_view)

        # Name
        self.app_name = QtWidgets.QLabel(self)
        self.app_name.set_text(
            desktop_file.as_dict['[Desktop Entry]']['Name'])
        self.layout_container.add_widget(self.app_name)

        self.set_style_sheet('background: rgba(255, 255, 255, 0.05);')

    def launch_app(self):
        print(self.app_name.text())

    def mouse_press_event(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.launch_app()
