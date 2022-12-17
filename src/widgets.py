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
    __clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)
    __leave_event_signal = QtCore.Signal(object)
    __mount_grid_signal = QtCore.Signal(object)

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
        self.__desktop_file_list = desktop_file_list
        self.__columns_num = columns_num
        self.__empty_lines = empty_lines

        # Style
        self.set_alignment(QtCore.Qt.AlignTop)
        self.set_contents_margins(0, 0, 0, 0)
        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background: transparent;')

        self.set_vertical_scroll_bar_policy(QtCore.Qt.ScrollBarAsNeeded)
        self.set_horizontal_scroll_bar_policy(QtCore.Qt.ScrollBarAlwaysOff)
        self.set_widget_resizable(True)  # ScrollBarAlwaysOn

        # Main layout
        self.__main_container = QtWidgets.QWidget()
        self.__main_container.set_contents_margins(0, 0, 0, 0)
        self.set_widget(self.__main_container)

        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.set_alignment(QtCore.Qt.AlignTop)
        self.__main_layout.set_contents_margins(0, 0, 0, 0)
        self.__main_layout.set_spacing(0)
        self.__main_container.set_layout(self.__main_layout)

        # Grid creation
        self.__line_layout = None
        mount_grid_thread = threading.Thread(
            target=self.__mount_grid_thread)
        mount_grid_thread.start()
        self.__mount_grid_signal.connect(self.__mount_grid)

    def clicked_signal(self) -> QtCore.Signal:
        """..."""
        return self.__clicked_signal

    def enter_event_signal(self) -> QtCore.Signal:
        """..."""
        return self.__enter_event_signal

    def leave_event_signal(self) -> QtCore.Signal:
        """..."""
        return self.__leave_event_signal

    def __mount_grid_thread(self) -> None:
        # Wait for the widget to render to assemble the app launcher
        time.sleep(0.05)
        self.__mount_grid_signal.emit(0)

    def __mount_grid(self) -> None:
        # Mount app launcher
        if not self.__desktop_file_list:
            self.__mount_ghost_grid()
            return

        for num, desktop_file in enumerate(self.__desktop_file_list):
            if num % self.__columns_num == 0:
                self.__line_layout = QtWidgets.QHBoxLayout()
                self.__line_layout.set_alignment(QtCore.Qt.AlignTop)
                self.__line_layout.set_contents_margins(0, 0, 0, 0)
                self.__line_layout.set_spacing(0)
                self.__main_layout.add_layout(self.__line_layout)

            if len(self.__desktop_file_list) < 7:
                app_launcher = AppLauncher(
                    desktop_file=desktop_file, no_thread=True)
            else:
                app_launcher = AppLauncher(desktop_file=desktop_file)
            app_launcher.clicked_signal().connect(
                self.__on_app_launcher_clicked_signal)
            app_launcher.enter_event_signal().connect(
                self.__on_launcher_enter_event_signal)
            app_launcher.leave_event_signal().connect(
                self.__on_launcher_leave_event_signal)
            self.__line_layout.add_widget(app_launcher)

        # Complete grid line
        missing_items_num = (
                self.__columns_num -
                (len(self.__desktop_file_list) % self.__columns_num))
        if missing_items_num != self.__columns_num:
            for item in range(missing_items_num):
                app_launcher = GhostAppLauncher()
                app_launcher.clicked_signal().connect(
                    self.__on_app_launcher_clicked_signal)
                self.__line_layout.add_widget(app_launcher)

        self.__main_layout.add_stretch(1)

    def __mount_ghost_grid(self):
        if self.__empty_lines:
            for _ in range(self.__empty_lines):
                self.__line_layout = QtWidgets.QHBoxLayout()
                self.__line_layout.set_alignment(QtCore.Qt.AlignTop)
                self.__line_layout.set_contents_margins(0, 0, 0, 0)
                self.__line_layout.set_spacing(0)
                self.__main_layout.add_layout(self.__line_layout)

                for item in range(self.__columns_num):
                    app_launcher = GhostAppLauncher()
                    app_launcher.clicked_signal().connect(
                        self.__on_app_launcher_clicked_signal)
                    self.__line_layout.add_widget(app_launcher)

            self.__main_layout.add_stretch(1)

    def __on_app_launcher_clicked_signal(self, widget) -> None:
        # When the app is clicked, this method is triggered
        self.__clicked_signal.emit(widget)

    def __on_launcher_enter_event_signal(self, widget) -> None:
        # ...
        self.enter_event_signal().emit(widget)

    def __on_launcher_leave_event_signal(self, widget) -> None:
        # ...
        self.leave_event_signal().emit(widget)


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget.

    Displays the application to launch.
    """
    __clicked_signal = QtCore.Signal(object)
    __right_clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)
    __leave_event_signal = QtCore.Signal(object)
    __mount_app_launcher_signal = QtCore.Signal(object)

    def __init__(
            self, desktop_file: DesktopFile, no_thread: bool = False,
            *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.__desktop_file = desktop_file
        self.__no_thread = no_thread

        # Self setting
        self.set_contents_margins(0, 0, 0, 0)
        self.set_fixed_height(150)

        # Style (TODO_ icon accent color)
        self.__bg_color_red, self.__bg_color_green, self.__bg_color_blue = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200))
        self.__style_sheet = (
            'background-color: rgba('
            f'{self.__bg_color_red}, '
            f'{self.__bg_color_green}, '
            f'{self.__bg_color_blue}, 0.05)')
        self.__style_sheet_hover = (
            'background-color: rgba('
            f'{self.__bg_color_red}, '
            f'{self.__bg_color_green}, '
            f'{self.__bg_color_blue}, 0.1)')

        # Main layout and container
        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.set_contents_margins(0, 0, 0, 0)
        self.__main_layout.set_spacing(0)
        self.set_layout(self.__main_layout)

        self.__main_container = QtWidgets.QWidget()
        self.__main_container.set_style_sheet(self.__style_sheet)
        self.__main_layout.add_widget(self.__main_container)

        # Body layout
        self.__body_layout = QtWidgets.QVBoxLayout()
        self.__body_layout.set_contents_margins(0, 30, 0, 0)
        self.__main_container.set_layout(self.__body_layout)

        # Accent
        self.__bottom_highlight_line = QtWidgets.QWidget()
        self.__main_layout.add_widget(self.__bottom_highlight_line)

        # Mount app laucher body (icon, name)
        if self.__no_thread:
            self.__mount_app_launcher()
        else:
            self.__mount_app_launcher_signal.connect(
                self.__mount_app_launcher)

            mount_app_launcher_thread = threading.Thread(
                target=self.__mount_app_launcher_thread)
            mount_app_launcher_thread.start()

    def desktop_file(self) -> DesktopFile:
        return self.__desktop_file

    def clicked_signal(self) -> QtCore.Signal:
        """..."""
        return self.__clicked_signal

    def right_clicked_signal(self) -> QtCore.Signal:
        """..."""
        return self.__right_clicked_signal

    def enter_event_signal(self) -> QtCore.Signal:
        """..."""
        return self.__enter_event_signal

    def leave_event_signal(self) -> QtCore.Signal:
        """..."""
        return self.__leave_event_signal

    def __mount_app_launcher_thread(self) -> None:
        # Wait for the widget to render to assemble the app launcher body
        time.sleep(0.1)
        self.__mount_app_launcher_signal.emit(0)

    def __mount_app_launcher(self) -> None:
        # Mount AppLauncher body

        # Icon
        icon_view = QtWidgets.QLabel()
        if 'Icon' in self.__desktop_file.content['[Desktop Entry]']:
            icon_path = IconTheme.getIconPath(
                iconname=self.__desktop_file.content[
                    '[Desktop Entry]']['Icon'],
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
        self.__body_layout.add_widget(icon_view)

        # Name
        app_name_layout = QtWidgets.QHBoxLayout()
        app_name_layout.set_contents_margins(0, 0, 0, 30)

        local, escope = (locale.getdefaultlocale()[0], '[Desktop Entry]')
        name_text = self.__desktop_file.content[escope]['Name']
        if f'Name[{local}]' in self.__desktop_file.content[escope]:
            name_text = self.__desktop_file.content[escope][f'Name[{local}]']

        app_name = ElidedLabel()
        app_name.set_text(name_text)
        app_name.set_alignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        app_name.set_style_sheet('background-color: transparent;')
        app_name.set_fixed_width(100)
        app_name_layout.add_widget(app_name)
        self.__body_layout.add_layout(app_name_layout)

        # Accent
        self.__bottom_highlight_line.set_style_sheet(self.__style_sheet)
        self.__bottom_highlight_line.set_fixed_height(5)

    def enter_event(self, event) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.
        """

        self.__main_container.set_style_sheet(self.__style_sheet_hover)
        self.__bottom_highlight_line.set_style_sheet(
            'background-color: rgba(255, 255, 255, 0.3);')
        self.__enter_event_signal.emit(self)
        event.ignore()

    def leave_event(self, event) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.
        """
        self.__main_container.set_style_sheet(self.__style_sheet)
        self.__bottom_highlight_line.set_style_sheet(self.__style_sheet)
        self.__leave_event_signal.emit(self)
        event.ignore()

    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)
        elif event.button() == QtCore.Qt.RightButton:
            print(self.__desktop_file, 'Right click')
            self.__right_clicked_signal.emit(self)

    def paint_event(self, event):
        img_path = None
        if 'snapd' in self.__desktop_file.url:
            img_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'static/snap.svg')
        elif 'flatpak' in self.__desktop_file.url:
            img_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'static/flatpak.svg')
        elif 'AppImage' in self.__desktop_file.content[
                '[Desktop Entry]']['Exec']:
            img_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'static/appimage.svg')

        if img_path:
            pixmap = QtGui.QPixmap(img_path)
            painter = QtGui.QPainter(self)
            painter.draw_pixmap(QtCore.QPoint(10, 10), pixmap)

        event.ignore()

    def __str__(self) -> str:
        return str(self.__desktop_file)


class GhostAppLauncher(QtWidgets.QWidget):
    """A bodiless widget

    Made to fill a row space when there are no more valid widgets to use.
    """
    __clicked_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        # self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_style_sheet('background-color: rgba(100, 100, 100, 0.05);')
        self.set_fixed_height(150)

        # Main layout
        self.__layout_container = QtWidgets.QVBoxLayout()
        self.__layout_container.set_alignment(QtCore.Qt.AlignCenter)
        self.__layout_container.set_contents_margins(1, 1, 1, 1)
        self.__layout_container.set_spacing(0)
        self.set_layout(self.__layout_container)

        # Icon
        self.__pixmap = QtGui.QPixmap(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'static/ghostapp.svg'))
        self.__pixmap = self.__pixmap.scaled(
            48, 48, QtCore.Qt.KeepAspectRatio)
        self.__icon_view = QtWidgets.QLabel(self)
        self.__icon_view.set_pixmap(self.__pixmap)
        self.__icon_view.set_alignment(QtCore.Qt.AlignCenter)
        self.__icon_view.set_size_policy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.__layout_container.add_widget(self.__icon_view)

        # Name
        self.__app_name = QtWidgets.QLabel()
        self.__app_name.set_text(' ')
        self.__app_name.set_alignment(QtCore.Qt.AlignHCenter)

    def clicked_signal(self) -> QtCore.Signal:
        """..."""
        return self.__clicked_signal

    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        # event -> QtGui.QMouseEvent
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def __str__(self) -> str:
        return '<GhostAppLauncher: Boo>'


class ElidedLabel(QtWidgets.QLabel):
    """A label widget that can display only the necessary text

    Hidden text is converted to an ellipsis.
    """
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
    __clicked_signal = QtCore.Signal(object)

    def __init__(
            self, text: str = '...', icon_name: str = None,
            *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.__text = text
        self.__icon_name = icon_name
        self.__state = False
        self.__enter_event_enabled = True

        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.set_contents_margins(0, 0, 0, 0)
        self.__main_layout.set_spacing(0)
        self.set_layout(self.__main_layout)

        self.__main_container = QtWidgets.QWidget()
        self.__main_container.set_contents_margins(0, 0, 0, 0)
        self.__main_container.set_style_sheet('background: transparent;')
        self.__main_layout.add_widget(self.__main_container)

        self.__body_layout = QtWidgets.QVBoxLayout()
        self.__body_layout.set_contents_margins(0, 0, 0, 0)
        self.__body_layout.set_spacing(0)
        self.__main_container.set_layout(self.__body_layout)

        # Icon and Text layout
        self.__text_layout = QtWidgets.QHBoxLayout()
        self.__text_layout.set_alignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        self.__text_layout.set_contents_margins(10, 0, 30, 0)
        self.__text_layout.set_spacing(0)
        self.__body_layout.add_layout(self.__text_layout)

        # Icon
        if self.__icon_name:
            icon_view = QtWidgets.QLabel()
            icon_path = IconTheme.getIconPath(
                iconname=self.__icon_name,
                size=22,
                theme='breeze-dark',
                extensions=['png', 'svg', 'xpm'])
            try:
                pixmap = QtGui.QPixmap(icon_path)
            except Exception as err:
                logging.error(err)
                pixmap = QtGui.QPixmap(os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'static/defaultapp.svg'))

            pixmap = pixmap.scaled(
                22, 22, QtCore.Qt.KeepAspectRatio)
            icon_view.set_pixmap(pixmap)

            icon_view.set_alignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
            icon_view.set_style_sheet('background-color: transparent;')
            self.__text_layout.add_widget(icon_view)

        # Text
        self.__text = QtWidgets.QLabel(self.__text)
        self.__text.set_contents_margins(20, 10, 5, 10)
        self.__text.set_style_sheet("""
            background: transparent;
            font-size: 16px;""")
        self.__text_layout.add_widget(self.__text)

        # Accent
        self.__bottom_highlight_line = QtWidgets.QWidget()
        self.__bottom_highlight_line.set_fixed_height(3)
        self.__bottom_highlight_line.set_style_sheet(
            'background: transparent;')
        self.__body_layout.add_widget(self.__bottom_highlight_line)

    def clicked_signal(self) -> QtCore.Signal:
        """..."""
        return self.__clicked_signal

    def check_state(self) -> bool:
        """Checks the state of the button

        Returns a boolean informing whether the button is active.
        """
        return self.__state

    def set_check_state(self, state: bool) -> None:
        """Configures the state of the button

        Receives a boolean to enable or disable the button state.

        Enabling the button state will keep the highlighted colors, and they
        will not be removed when the mouse is moved outside the widget.

        Disabling the button state will return the default behavior.

        :param state: a boolean to enable or disable the button state
        """
        self.__state = state
        if state:
            self.__main_container.set_style_sheet("""
                background-color: rgba(255, 255, 255, 0.1);""")
            self.__bottom_highlight_line.set_style_sheet("""
                background-color: rgba(255, 255, 255, 0.3);""")
        else:
            self.__main_container.set_style_sheet("""
                background: transparent;""")
            self.__bottom_highlight_line.set_style_sheet("""
                background: transparent;""")

    def text(self) -> str:
        """..."""
        return self.__text.text()

    def set_enter_event_enabled(self, disbled: bool) -> None:
        """..."""
        self.__enter_event_enabled = disbled

    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def enter_event(self, event) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.
        """
        if self.__enter_event_enabled:
            if not self.__state:
                self.__main_container.set_style_sheet("""
                    background-color: rgba(255, 255, 255, 0.05);""")
            self.__clicked_signal.emit(self)
            event.ignore()

    def leave_event(self, event) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.
        """
        if self.__enter_event_enabled:
            if not self.__state:
                self.__main_container.set_style_sheet("""
                    background: transparent;""")
            event.ignore()


class EnergyButton(QtWidgets.QWidget):
    """Button widget

    A custom button to use for category pagination.
    """
    __clicked_signal = QtCore.Signal(object)

    def __init__(
            self,
            icon_name: str, name_id: str = None,
            *args, **kwargs) -> None:
        """Class constructor."""
        super().__init__(*args, **kwargs)
        self.__icon_name = icon_name
        self.__name_id = name_id if name_id else self.__icon_name
        self.__enter_event_enabled = True

        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.set_contents_margins(0, 0, 0, 0)
        self.__main_layout.set_spacing(0)
        self.set_layout(self.__main_layout)

        self.__icon_view = QtWidgets.QLabel()
        self.__icon_view.set_fixed_height(80)
        self.__icon_view.set_fixed_width(80)
        self.__icon_view.set_contents_margins(0, 0, 0, 0)
        self.__icon_view.set_alignment(QtCore.Qt.AlignCenter)
        self.__icon_view.set_style_sheet('background-color: transparent;')

        icon_path = IconTheme.getIconPath(
            iconname=self.__icon_name,
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
        self.__icon_view.set_pixmap(scaled_pixmap)
        self.__main_layout.add_widget(self.__icon_view)

    def name_id(self) -> str:
        """..."""
        return self.__name_id

    def icon_name(self) -> str:
        """..."""
        return self.__icon_name

    def set_enter_event_enabled(self, disbled: bool) -> None:
        """..."""
        self.__enter_event_enabled = disbled

    def clicked_signal(self) -> QtCore.Signal:
        """..."""
        return self.__clicked_signal

    def mouse_press_event(self, event) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def enter_event(self, event) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.
        """
        if self.__enter_event_enabled:
            self.__icon_view.set_style_sheet("""
                border-radius: 40px;
                background-color: rgba(255, 255, 255, 0.05);""")
        event.ignore()

    def leave_event(self, event) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.
        """
        if self.__enter_event_enabled:
            self.__icon_view.set_style_sheet('background: transparent;')
        event.ignore()


class SearchApps(QtWidgets.QLineEdit):
    """..."""
    text_changed = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)
        self.set_style_sheet("""
            color: #AAA;
            font-size: 20px;
            background: transparent;
            border: 0px;
            padding: 10px;""")
        self.textChanged.connect(lambda text: self.text_changed.emit(text))

    def mouse_press_event(self, event):
        """..."""
        if (event.button() == QtCore.Qt.LeftButton
                or event.button() == QtCore.Qt.RightButton):
            print(self)
