#!/usr/bin env python3
import logging
from xdg import IconTheme

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

from attachments import DesktopFile, MenuSchema


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
        if 'Icon' in self.desktop_file.as_dict['[Desktop Entry]']:
            self.icon_path = IconTheme.getIconPath(
                iconname=self.desktop_file.as_dict['[Desktop Entry]']['Icon'],
                size=48,
                theme='breeze',
                extensions=['png', 'svg', 'xpm'])
            try:
                self.pixmap = QtGui.QPixmap(self.icon_path)
            except Exception as err:
                logging.error(err)
                self.pixmap = QtGui.QPixmap(
                    '/usr/share/icons/breeze/apps/48/alienarena.svg')

            self.scaled_pixmap = self.pixmap.scaled(
                48, 48, QtCore.Qt.KeepAspectRatio)
            self.icon_view = QtWidgets.QLabel(self)
            self.icon_view.set_pixmap(self.scaled_pixmap)
            self.icon_view.set_alignment(QtCore.Qt.AlignCenter)
            self.layout_container.add_widget(self.icon_view)

        # Name
        self.app_name = QtWidgets.QLabel()
        self.app_name.set_text(
            self.desktop_file.as_dict['[Desktop Entry]']['Name'])
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


class AppGrid(QtWidgets.QScrollArea):
    """App launcher widget."""
    clicked = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(self, *args, **kwargs):
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.menu_schema = MenuSchema()
        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOn)
        self.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOff)
        self.set_widget_resizable(True)

        self.widget = QtWidgets.QWidget()
        self.set_widget(self.widget)

        self.layout_container = QtWidgets.QVBoxLayout()
        self.widget.set_layout(self.layout_container)

        for item in self.menu_schema.as_dict['All']:
            app_launcher = AppLauncher(item)
            app_launcher.clicked.connect(self.app_launcher_was_clicked)
            self.layout_container.add_widget(app_launcher)

    @QtCore.Slot()
    def app_launcher_was_clicked(self, widget):
        self.clicked.emit(widget)


class ElidedLabel(QtWidgets.QLabel):
    @QtCore.Slot()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(
            self.text(), QtCore.Qt.ElideRight, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)
