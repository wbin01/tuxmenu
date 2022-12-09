#!/usr/bin env python3
import logging
import os.path

from xdg import IconTheme

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

from attachments import DesktopFile, MenuSchema


class AppGrid(QtWidgets.QScrollArea):
    """App launcher grid widget."""
    clicked = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(
            self,
            desktop_file_list: list,
            columns_num: int = 4,
            *args, **kwargs):
        """Class constructor.

        :param desktop_file_list: [DesktopFile, DesktopFile]
        :param columns_num: Number of grid columns, default is 4
        """
        super().__init__(*args, **kwargs)
        self.desktop_file_list = desktop_file_list
        self.columns_num = columns_num

        # AppGrid settings
        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOn)
        self.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOff)
        self.set_widget_resizable(True)

        self.widget = QtWidgets.QWidget()
        self.set_widget(self.widget)

        self.layout_container = QtWidgets.QVBoxLayout()
        self.widget.set_layout(self.layout_container)

        self.line_layout = None
        for num, desktop_file in enumerate(self.desktop_file_list):
            if num % self.columns_num == 0:
                self.line_layout = QtWidgets.QHBoxLayout()
                self.layout_container.add_layout(self.line_layout)

            app_launcher = AppLauncher(desktop_file)
            app_launcher.clicked.connect(self.app_launcher_was_clicked)
            self.line_layout.add_widget(app_launcher)

        # Complete line
        missing_items_num = (
            self.columns_num -
            (len(self.desktop_file_list) % self.columns_num))
        if missing_items_num != self.columns_num:
            for item in range(missing_items_num):
                app_launcher = GhostAppLauncher()
                app_launcher.clicked.connect(self.app_launcher_was_clicked)
                self.line_layout.add_widget(app_launcher)

    @QtCore.Slot()
    def app_launcher_was_clicked(self, widget):
        self.clicked.emit(widget)


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget."""
    clicked = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(self, desktop_file: DesktopFile, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.desktop_file = desktop_file

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_spacing(0)
        self.set_layout(self.layout_container)

        # Icon
        self.default_icon_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'static/defaultapp.svg')

        if 'Icon' in self.desktop_file.content['[Desktop Entry]']:
            self.icon_path = IconTheme.getIconPath(
                iconname=self.desktop_file.content['[Desktop Entry]']['Icon'],
                size=48,
                theme='breeze',
                extensions=['png', 'svg', 'xpm'])
            try:
                self.pixmap = QtGui.QPixmap(self.icon_path)
            except Exception as err:
                logging.error(err)
                self.pixmap = QtGui.QPixmap(self.default_icon_path)

            self.scaled_pixmap = self.pixmap.scaled(
                48, 48, QtCore.Qt.KeepAspectRatio)
            self.icon_view = QtWidgets.QLabel(self)
            self.icon_view.set_pixmap(self.scaled_pixmap)
            self.icon_view.set_alignment(QtCore.Qt.AlignCenter)
            self.layout_container.add_widget(self.icon_view)

        # Name
        self.app_name = QtWidgets.QLabel()
        self.app_name.set_text(
            self.desktop_file.content['[Desktop Entry]']['Name'])
        self.layout_container.add_widget(self.app_name)

        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

    @QtCore.Slot()
    def mouse_press_event(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)
            event.ignore()

    def __str__(self) -> str:
        return str(self.desktop_file)


class GhostAppLauncher(QtWidgets.QWidget):
    """App launcher widget."""
    clicked = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_spacing(0)
        self.set_layout(self.layout_container)

        # Icon
        self.pixmap = QtGui.QPixmap(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'static/ghostapp.svg'))
        self.scaled_pixmap = self.pixmap.scaled(
            48, 48, QtCore.Qt.KeepAspectRatio)
        self.icon_view = QtWidgets.QLabel(self)
        self.icon_view.set_pixmap(self.scaled_pixmap)
        self.icon_view.set_alignment(QtCore.Qt.AlignCenter)
        self.layout_container.add_widget(self.icon_view)

        # Name
        self.app_name = QtWidgets.QLabel()
        self.app_name.set_text(' ')

        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

    @QtCore.Slot()
    def mouse_press_event(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)
            event.ignore()

    def __str__(self) -> str:
        return '<GhostAppLauncher: Boo>'


class ElidedLabel(QtWidgets.QLabel):
    @QtCore.Slot()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(
            self.text(), QtCore.Qt.ElideRight, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)
