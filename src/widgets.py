#!/usr/bin env python3
import locale
import logging
import os.path
import random
import threading
import time

from xdg import IconTheme

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

from attachments import DesktopFile, MenuSchema


class AppGrid(QtWidgets.QScrollArea):
    """App launcher grid widget."""
    clicked = QtCore.Signal(QtGui.QMouseEvent)
    mount_app_launcher_signal = QtCore.Signal(object)

    def __init__(
            self,
            desktop_file_list: list,
            columns_num: int = 5,
            empty_lines: int = 0,
            *args, **kwargs) -> None:
        """Class constructor.

        :param desktop_file_list: [DesktopFile, DesktopFile]
        :param columns_num: Number of grid columns, default is 5
        """
        super().__init__(*args, **kwargs)
        self.desktop_file_list = desktop_file_list
        self.columns_num = columns_num
        self.empty_lines = empty_lines

        # Style
        self.set_alignment(QtCore.Qt.AlignTop)
        self.set_contents_margins(0, 0, 0, 0)
        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarAsNeeded)
        self.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOff)
        self.set_widget_resizable(True)  # ScrollBarAlwaysOn

        # Main layout
        self.main_container = QtWidgets.QWidget()
        self.main_container.set_contents_margins(0, 0, 0, 0)
        self.set_widget(self.main_container)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.set_alignment(QtCore.Qt.AlignTop)
        self.main_layout.set_contents_margins(0, 0, 0, 0)
        self.main_layout.set_spacing(0)
        self.main_container.set_layout(self.main_layout)

        # Grid creation
        self.line_layout = None

        mount_app_launcher_thread = threading.Thread(
            target=self.__mount_grid_thread)
        mount_app_launcher_thread.start()

        self.mount_app_launcher_signal.connect(
            self.__mount_grid)

    @QtCore.Slot()
    def __mount_grid_thread(self) -> None:
        # Wait for the widget to render to assemble the app launcher
        if len(self.desktop_file_list) < 10:
            time.sleep(0.01)
            self.mount_app_launcher_signal.emit(0)
        else:
            time.sleep(0.07)
            self.mount_app_launcher_signal.emit(0)

    @QtCore.Slot()
    def __mount_grid(self) -> None:
        # Mount app launcher
        if not self.desktop_file_list:
            self.__mount_a_ghost_grid()
            return

        for num, desktop_file in enumerate(self.desktop_file_list):
            if num % self.columns_num == 0:
                self.line_layout = QtWidgets.QHBoxLayout()
                self.line_layout.set_alignment(QtCore.Qt.AlignTop)
                self.line_layout.set_contents_margins(0, 0, 0, 0)
                self.line_layout.set_spacing(0)
                self.main_layout.add_layout(self.line_layout)

            if len(self.desktop_file_list) < 7:
                app_launcher = AppLauncher(
                    desktop_file=desktop_file, no_thread=True)
            else:
                app_launcher = AppLauncher(desktop_file=desktop_file)
            app_launcher.clicked.connect(
                self.__on_app_launcher_was_clicked_signal)
            self.line_layout.add_widget(app_launcher)

        # Complete grid line
        missing_items_num = (
            self.columns_num -
            (len(self.desktop_file_list) % self.columns_num))
        if missing_items_num != self.columns_num:
            for item in range(missing_items_num):
                app_launcher = GhostAppLauncher()
                app_launcher.clicked.connect(
                    self.__on_app_launcher_was_clicked_signal)
                self.line_layout.add_widget(app_launcher)

        self.main_layout.add_stretch(1)

    @QtCore.Slot()
    def __mount_a_ghost_grid(self):
        if self.empty_lines:
            for _ in range(self.empty_lines):
                self.line_layout = QtWidgets.QHBoxLayout()
                self.line_layout.set_alignment(QtCore.Qt.AlignTop)
                self.line_layout.set_contents_margins(0, 0, 0, 0)
                self.line_layout.set_spacing(0)
                self.main_layout.add_layout(self.line_layout)

                for item in range(self.columns_num):
                    app_launcher = GhostAppLauncher()
                    app_launcher.clicked.connect(
                        self.__on_app_launcher_was_clicked_signal)
                    self.line_layout.add_widget(app_launcher)

            self.main_layout.add_stretch(1)

    @QtCore.Slot()
    def __on_app_launcher_was_clicked_signal(self, widget) -> None:
        # When the app is clicked, this method is triggered
        self.clicked.emit(widget)


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget.

    Displays the application to launch.
    """
    clicked = QtCore.Signal(object)
    mount_app_launcher_signal = QtCore.Signal(object)

    def __init__(
            self, desktop_file: DesktopFile, no_thread: bool = False,
            *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.desktop_file = desktop_file
        self.no_thread = no_thread

        # Self setting
        self.set_contents_margins(0, 0, 0, 0)
        self.set_fixed_height(150)

        # Style (TODO_ icon accent color)
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

        # Main layout and container
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.set_contents_margins(0, 0, 0, 0)
        self.main_layout.set_spacing(0)
        self.set_layout(self.main_layout)

        self.main_container = QtWidgets.QWidget()
        self.main_container.set_style_sheet(self.style_sheet)
        self.main_layout.add_widget(self.main_container)

        # Body layout
        self.body_layout = QtWidgets.QVBoxLayout()
        self.body_layout.set_contents_margins(0, 30, 0, 0)
        self.main_container.set_layout(self.body_layout)

        # Accent
        self.bottom_highlight_line = QtWidgets.QWidget()
        self.main_layout.add_widget(self.bottom_highlight_line)

        # Mount app laucher body (icon, name)
        if self.no_thread:
            self.__mount_app_launcher()
        else:
            self.mount_app_launcher_signal.connect(
                self.__mount_app_launcher)

            self.mount_app_launcher_thread = threading.Thread(
                target=self.__mount_app_launcher_thread)
            self.mount_app_launcher_thread.start()

    @QtCore.Slot()
    def __mount_app_launcher_thread(self) -> None:
        # Wait for the widget to render to assemble the app launcher body
        time.sleep(0.1)
        self.mount_app_launcher_signal.emit(0)

    @QtCore.Slot()
    def __mount_app_launcher(self) -> None:
        # Mount AppLauncher body

        # Icon
        icon_view = QtWidgets.QLabel()
        if 'Icon' in self.desktop_file.content['[Desktop Entry]']:
            icon_path = IconTheme.getIconPath(
                iconname=self.desktop_file.content['[Desktop Entry]']['Icon'],
                size=48,
                theme='breeze-dark',
                extensions=['png', 'svg', 'xpm'])
            try:
                pixmap = QtGui.QPixmap(icon_path)
            except Exception as err:
                logging.error(err)
                pixmap = QtGui.QPixmap(os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'static/defaultapp.svg'))

            scaled_pixmap = pixmap.scaled(
                48, 48, QtCore.Qt.KeepAspectRatio)
            icon_view.set_pixmap(scaled_pixmap)

        icon_view.set_alignment(QtCore.Qt.AlignCenter)
        icon_view.set_style_sheet('background-color: transparent;')
        icon_view.set_size_policy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.body_layout.add_widget(icon_view)

        # Name
        app_name_layout = QtWidgets.QHBoxLayout()
        app_name_layout.set_contents_margins(0, 0, 0, 30)
        app_name = ElidedLabel()
        app_name.set_alignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        app_name.set_text(self.desktop_file.content['[Desktop Entry]']['Name'])
        app_name.set_style_sheet('background-color: transparent;')
        app_name.set_fixed_width(100)
        app_name_layout.add_widget(app_name)
        self.body_layout.add_layout(app_name_layout)

        # Accent
        self.bottom_highlight_line.set_style_sheet(self.style_sheet)
        self.bottom_highlight_line.set_fixed_height(5)

    @QtCore.Slot()
    def enter_event(self, event) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.
        """

        self.main_container.set_style_sheet(self.style_sheet_hover)
        self.bottom_highlight_line.set_style_sheet(
            'background-color: rgba(255, 255, 255, 0.3);')
        # Generic name to send
        local_name = f'GenericName[{locale.getdefaultlocale()[0]}]'
        if local_name in self.desktop_file.content['[Desktop Entry]']:
            name = self.desktop_file.content['[Desktop Entry]'][local_name]
        elif 'GenericName' in self.desktop_file.content['[Desktop Entry]']:
            name = self.desktop_file.content['[Desktop Entry]']['GenericName']
        else:
            name = self.desktop_file.content['[Desktop Entry]']['Name']
        logging.info(name)
        event.ignore()

    @QtCore.Slot()
    def leave_event(self, event) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.
        """
        self.main_container.set_style_sheet(self.style_sheet)
        self.bottom_highlight_line.set_style_sheet(self.style_sheet)
        event.ignore()

    @QtCore.Slot()
    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)

    def __str__(self) -> str:
        return str(self.desktop_file)


class GhostAppLauncher(QtWidgets.QWidget):
    """A bodiless widget

    Made to fill a row space when there are no more valid widgets to use.
    """
    clicked = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        # self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
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
    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        # event -> QtGui.QMouseEvent
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)

    def __str__(self) -> str:
        return '<GhostAppLauncher: Boo>'


class ElidedLabel(QtWidgets.QLabel):
    """A label widget that can display only the necessary text

    Hidden text is converted to an ellipsis.
    """
    @QtCore.Slot()
    def paint_event(self, event) -> None:
        """Event that draws the text

        Calculate the size of the text that can be displayed and convert
        the rest to an ellipsis.
        """
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elided_text(
            self.text(), QtCore.Qt.ElideRight, self.width())
        painter.draw_text(self.rect(), self.alignment(), elided)
        event.ignore()


class CategoryButton(QtWidgets.QWidget):
    """Button widget

    A custom button to use for category pagination.
    """
    clicked = QtCore.Signal(object)

    def __init__(
            self, text: str = '...', icon_name: str = None,
            *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.text = text
        self.icon_name = icon_name
        self.state = False

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.set_contents_margins(0, 0, 0, 0)
        self.main_layout.set_spacing(0)
        self.set_layout(self.main_layout)

        self.main_container = QtWidgets.QWidget()
        self.main_container.set_contents_margins(0, 0, 0, 0)
        self.main_container.set_style_sheet('background: transparent;')
        self.main_layout.add_widget(self.main_container)

        self.body_layout = QtWidgets.QVBoxLayout()
        self.body_layout.set_contents_margins(0, 0, 0, 0)
        self.body_layout.set_spacing(0)
        self.main_container.set_layout(self.body_layout)

        # Icon and Text layout
        self.text_layout = QtWidgets.QHBoxLayout()
        self.text_layout.set_alignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        self.text_layout.set_contents_margins(10, 0, 30, 0)
        self.text_layout.set_spacing(0)
        self.body_layout.add_layout(self.text_layout)

        # Icon
        if self.icon_name:
            icon_view = QtWidgets.QLabel()
            icon_path = IconTheme.getIconPath(
                iconname=self.icon_name,
                size=48,
                theme='breeze-dark',
                extensions=['png', 'svg', 'xpm'])
            try:
                pixmap = QtGui.QPixmap(icon_path)
            except Exception as err:
                logging.error(err)
                pixmap = QtGui.QPixmap(os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'static/defaultapp.svg'))

            scaled_pixmap = pixmap.scaled(
                32, 32, QtCore.Qt.KeepAspectRatio)
            icon_view.set_pixmap(scaled_pixmap)

            icon_view.set_alignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
            icon_view.set_style_sheet('background-color: transparent;')
            self.text_layout.add_widget(icon_view)

        self.text = QtWidgets.QLabel(self.text)
        self.text.set_contents_margins(20, 10, 5, 10)
        self.text.set_style_sheet("""
            background: transparent;
            font-size: 18px;""")
        self.text_layout.add_widget(self.text)

        # Accent
        self.bottom_highlight_line = QtWidgets.QWidget()
        self.bottom_highlight_line.set_fixed_height(3)
        self.bottom_highlight_line.set_style_sheet('background: transparent;')
        self.body_layout.add_widget(self.bottom_highlight_line)

    @QtCore.Slot()
    def check_state(self) -> bool:
        """Checks the state of the button

        Returns a boolean informing whether the button is active.
        """
        return self.state

    @QtCore.Slot()
    def set_check_state(self, state: bool) -> None:
        """Configures the state of the button

        Receives a boolean to enable or disable the button state.

        Enabling the button state will keep the highlighted colors, and they
        will not be removed when the mouse is moved outside the widget.

        Disabling the button state will return the default behavior.

        :param state: a boolean to enable or disable the button state
        """
        self.state = state
        if state:
            self.main_container.set_style_sheet("""
                background-color: rgba(255, 255, 255, 0.1);""")
            self.bottom_highlight_line.set_style_sheet("""
                background-color: rgba(255, 255, 255, 0.3);""")
        else:
            self.main_container.set_style_sheet("""
                background: transparent;""")
            self.bottom_highlight_line.set_style_sheet("""
                background: transparent;""")

    @QtCore.Slot()
    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)
            event.ignore()

    @QtCore.Slot()
    def enter_event(self, event) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.
        """
        if not self.state:
            self.main_container.set_style_sheet("""
                background-color: rgba(255, 255, 255, 0.05);""")
        self.clicked.emit(self)
        event.ignore()

    @QtCore.Slot()
    def leave_event(self, event) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.
        """
        if not self.state:
            self.main_container.set_style_sheet("""
                background: transparent;""")
        event.ignore()


class EnergyButton(QtWidgets.QWidget):
    """Button widget

    A custom button to use for category pagination.
    """
    clicked = QtCore.Signal(object)

    def __init__(self, icon_name: str, *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.icon_name = icon_name

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.set_contents_margins(0, 0, 0, 0)
        self.main_layout.set_spacing(0)
        self.set_layout(self.main_layout)

        self.icon_view = QtWidgets.QLabel()
        self.icon_view.set_fixed_height(80)
        self.icon_view.set_fixed_width(80)
        self.icon_view.set_contents_margins(0, 0, 0, 0)
        self.icon_view.set_alignment(QtCore.Qt.AlignCenter)
        self.icon_view.set_style_sheet('background-color: transparent;')

        icon_path = IconTheme.getIconPath(
            iconname=self.icon_name,
            size=48,
            theme='breeze-dark',
            extensions=['png', 'svg', 'xpm'])
        try:
            pixmap = QtGui.QPixmap(icon_path)
        except Exception as err:
            logging.error(err)
            pixmap = QtGui.QPixmap(os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'static/defaultapp.svg'))

        scaled_pixmap = pixmap.scaled(
            32, 32, QtCore.Qt.KeepAspectRatio)
        self.icon_view.set_pixmap(scaled_pixmap)
        self.main_layout.add_widget(self.icon_view)

    @QtCore.Slot()
    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)
            event.ignore()

    @QtCore.Slot()
    def enter_event(self, event) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.
        """
        self.icon_view.set_style_sheet("""
            border-radius: 40px;
            background-color: rgba(255, 255, 255, 0.05);""")
        event.ignore()

    @QtCore.Slot()
    def leave_event(self, event) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.
        """
        self.icon_view.set_style_sheet('background: transparent;')
        event.ignore()
