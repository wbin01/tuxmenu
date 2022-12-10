#!/usr/bin env python3
import logging
import os.path
import random

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
            columns_num: int = 5,
            *args, **kwargs):
        """Class constructor.

        :param desktop_file_list: [DesktopFile, DesktopFile]
        :param columns_num: Number of grid columns, default is 5
        """
        super().__init__(*args, **kwargs)
        self.desktop_file_list = desktop_file_list
        self.columns_num = columns_num

        # Style
        self.set_contents_margins(0, 0, 0, 0)
        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarAsNeeded)
        self.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOff)
        self.set_widget_resizable(True)  # ScrollBarAlwaysOn

        # Main layout
        self.widget = QtWidgets.QWidget()
        self.widget.set_contents_margins(0, 0, 0, 0)
        self.set_widget(self.widget)

        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_contents_margins(0, 0, 0, 0)
        self.layout_container.set_spacing(0)
        self.widget.set_layout(self.layout_container)

        # Grid creation
        self.line_layout = None
        for num, desktop_file in enumerate(self.desktop_file_list):
            if num % self.columns_num == 0:
                self.line_layout = QtWidgets.QHBoxLayout()
                self.line_layout.set_alignment(QtCore.Qt.AlignTop)
                self.line_layout.set_contents_margins(0, 0, 0, 0)
                self.line_layout.set_spacing(0)
                self.layout_container.add_layout(self.line_layout)

            app_launcher = AppLauncher(desktop_file)
            app_launcher.clicked.connect(self.app_launcher_was_clicked)
            self.line_layout.add_widget(app_launcher)

        # Complete grid line
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
        """..."""
        self.clicked.emit(widget)


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget."""
    clicked = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(self, desktop_file: DesktopFile, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.desktop_file = desktop_file

        # Style
        self.set_contents_margins(0, 0, 0, 0)
        self.set_fixed_height(150)
        self.bg_color_red, self.bg_color_green, self.bg_color_blue = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200))
        self.style_sheet = (
            'background-color: rgba('
            f'{self.bg_color_red}, '
            f'{self.bg_color_green}, '
            f'{self.bg_color_blue}, 0.05)')
        self.style_sheet_hover = (
            'background-color: rgba('
            f'{self.bg_color_red}, '
            f'{self.bg_color_green}, '
            f'{self.bg_color_blue}, 0.1)')

        # Main layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.set_contents_margins(0, 0, 0, 0)
        self.layout.set_spacing(0)
        self.set_layout(self.layout)

        self.widget_container = QtWidgets.QWidget()
        self.widget_container.set_style_sheet(self.style_sheet)
        self.layout.add_widget(self.widget_container)

        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_contents_margins(0, 30, 0, 0)
        self.widget_container.set_layout(self.layout_container)

        # Icon
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
                self.pixmap = QtGui.QPixmap(os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'static/defaultapp.svg'))

            self.scaled_pixmap = self.pixmap.scaled(
                48, 48, QtCore.Qt.KeepAspectRatio)
            self.icon_view = QtWidgets.QLabel(self)
            self.icon_view.set_style_sheet('background-color: transparent;')
            self.icon_view.set_size_policy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
            self.icon_view.set_pixmap(self.scaled_pixmap)
            self.icon_view.set_alignment(QtCore.Qt.AlignCenter)
            self.layout_container.add_widget(self.icon_view)

        # Name
        self.app_name_layout = QtWidgets.QHBoxLayout()
        self.app_name_layout.set_contents_margins(0, 0, 0, 30)
        self.layout_container.add_layout(self.app_name_layout)

        self.app_name = ElidedLabel()
        self.app_name.set_alignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.app_name.set_text(
            self.desktop_file.content['[Desktop Entry]']['Name'])
        self.app_name.set_style_sheet('background-color: transparent;')
        self.app_name.set_fixed_width(100)
        self.app_name_layout.add_widget(self.app_name)

        # Accent
        self.accent_widget = QtWidgets.QWidget()
        self.accent_widget.set_style_sheet(self.style_sheet)
        self.accent_widget.set_fixed_height(5)
        self.layout.add_widget(self.accent_widget)

    def enter_event(self, event):
        """..."""
        self.widget_container.set_style_sheet(self.style_sheet_hover)
        self.accent_widget.set_style_sheet(
            'background-color: rgba(255, 255, 255, 0.3);')
        event.ignore()

    def leave_event(self, event):
        """..."""
        self.widget_container.set_style_sheet(self.style_sheet)
        self.accent_widget.set_style_sheet(self.style_sheet)
        event.ignore()

    @QtCore.Slot()
    def mouse_press_event(self, event):
        """..."""
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
        # self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        # self.set_style_sheet('background: transparent;')
        self.set_style_sheet('background-color: rgba(100, 100, 100, 0.05);')
        self.set_fixed_height(150)

        # Main layout
        self.layout_container = QtWidgets.QVBoxLayout()
        self.layout_container.set_alignment(QtCore.Qt.AlignCenter)
        self.layout_container.set_contents_margins(1, 1, 1, 1)
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
        self.icon_view.set_size_policy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.layout_container.add_widget(self.icon_view)

        # Name
        self.app_name = QtWidgets.QLabel()
        self.app_name.set_text(' ')
        self.app_name.set_alignment(QtCore.Qt.AlignHCenter)

    @QtCore.Slot()
    def mouse_press_event(self, event):
        """..."""
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)
            event.ignore()

    def __str__(self) -> str:
        return '<GhostAppLauncher: Boo>'


class ElidedLabel(QtWidgets.QLabel):
    """..."""
    def paint_event(self, event):
        """..."""
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elided_text(
            self.text(), QtCore.Qt.ElideRight, self.width())
        painter.draw_text(self.rect(), self.alignment(), elided)

        event.ignore()
