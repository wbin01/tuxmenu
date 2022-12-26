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


class AppLauncherContextMenuButton(QtWidgets.QWidget):
    """Button widget

    A custom button to use for category pagination.
    """
    __clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)

    def __init__(
            self, text: str = None, icon_name: str = None,
            button_id: str = None, *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.

        :param text: Text that will be displayed on the button
        :param icon_name: Name of the icon that will be displayed on the button
        :param button_id: ID set manually
        """
        super().__init__(*args, **kwargs)
        self.set_style_sheet(
            'background-color: rgba(255, 255, 255, 0.05); font-size: 14px;')

        self.__text = text
        self.__icon_name = icon_name
        self.__button_id = button_id if button_id else str(id(self))

        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.set_contents_margins(0, 0, 0, 0)
        self.__main_layout.set_spacing(0)
        self.set_layout(self.__main_layout)

        # Icon and Text layout
        self.__text_layout = QtWidgets.QHBoxLayout()
        self.__text_layout.set_alignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        self.__text_layout.set_contents_margins(0, 0, 0, 0)
        self.__text_layout.set_spacing(0)
        self.__main_layout.add_layout(self.__text_layout)

        # Icon
        self.__icon_view = QtWidgets.QLabel()
        self.__icon_view.set_contents_margins(5, 0, 0, 0)
        self.__icon_view.set_alignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
        if self.__icon_name:
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
            self.__icon_view.set_pixmap(pixmap)
            self.__text_layout.add_widget(self.__icon_view)

        # Text
        self.__text_label = QtWidgets.QLabel(self.__text)
        self.__text_label.set_contents_margins(5, 0, 5, 0)
        self.__text_label.set_size_policy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.__text_layout.add_widget(self.__text_label)

    def clicked_signal(self) -> QtCore.Signal:
        """Mouse button click signal

        Gets the signal that is emitted when a mouse button is pressed.
        """
        return self.__clicked_signal

    def text(self) -> str:
        """Widget text

        Gets the text used in the widget.
        """
        return self.__text_label.text()

    def button_id(self) -> str:
        """Button ID

        Gets the identifier of the button that was defined by parameter.
        """
        return self.__button_id

    def enter_event_signal(self) -> QtCore.Signal:
        """Mouse hover event

        Gets the signal that is emitted when the mouse hovers over the widget.
        """
        return self.__enter_event_signal

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget

        Emits a signal that the widget has been clicked.

        :param event: QEvent received by sent signal
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def enter_event(self, event: QtCore.QEvent) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.

        :param event: QEvent received by sent signal
        """
        self.set_style_sheet(
            'font-size: 14px; background-color: rgba(255, 255, 255, 0.1);')
        self.__enter_event_signal.emit(self)
        event.ignore()

    def leave_event(self, event: QtCore.QEvent) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.

        :param event: QEvent received by sent signal
        """
        self.set_style_sheet(
            'font-size: 14px; background-color: rgba(255, 255, 255, 0.05);')
        event.ignore()

    def __str__(self) -> str:
        return f'<AppLauncherContextMenuButton: {self.__text}>'


class AppLauncherContextMenu(QtWidgets.QWidget):
    """Application launcher context menu widget"""
    __clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)

    def __init__(
            self,
            desktop_file: DesktopFile,
            pin_desktop_file_list: list,
            *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.

        :param desktop_file: DesktopFile object
        :param pin_desktop_file_list: list of pinned DesktopFile objects
        """
        super().__init__(*args, **kwargs)
        self.__desktop_file = desktop_file
        self.__pin_desktop_file_list = pin_desktop_file_list

        self.set_style_sheet('background-color: rgba(100, 100, 100, 0.05);')

        # Main layout
        self.__layout_container = QtWidgets.QVBoxLayout()
        self.__layout_container.set_alignment(QtCore.Qt.AlignCenter)
        self.__layout_container.set_contents_margins(0, 0, 0, 0)
        self.__layout_container.set_spacing(0)
        self.set_layout(self.__layout_container)

        body = QtWidgets.QWidget()
        body.set_size_policy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.__layout_container.add_widget(body)

        body_layout = QtWidgets.QVBoxLayout()
        body_layout.set_contents_margins(5, 5, 5, 5)
        body_layout.set_spacing(1)
        body.set_layout(body_layout)

        # Back buttons
        back = AppLauncherContextMenuButton(
            text=' ', icon_name='go-previous', button_id='go-back')
        back.clicked_signal().connect(self.__on_button)
        back.enter_event_signal().connect(self.__on_button_enter_event)
        body_layout.add_widget(back)

        # Action button
        desktop_file_urls = [x.url for x in self.__pin_desktop_file_list]

        self.__pin_remove_button = AppLauncherContextMenuButton(
            text='Unpin', icon_name='window-unpin', button_id='unpin')
        self.__pin_remove_button.clicked_signal().connect(
            self.__on_button)
        self.__pin_remove_button.enter_event_signal().connect(
            self.__on_button_enter_event)
        body_layout.add_widget(self.__pin_remove_button)
        if self.__desktop_file.url not in desktop_file_urls:
            self.__pin_remove_button.set_visible(False)

        self.__pin_button = AppLauncherContextMenuButton(
            text='Pin', icon_name='window-pin', button_id='pin')
        self.__pin_button.clicked_signal().connect(self.__on_button)
        self.__pin_button.enter_event_signal().connect(
            self.__on_button_enter_event)
        body_layout.add_widget(self.__pin_button)
        if self.__desktop_file.url in desktop_file_urls:
            self.__pin_button.set_visible(False)

        shortcut = AppLauncherContextMenuButton(
            text='Shortcut', icon_name='link', button_id='shortcut')
        shortcut.clicked_signal().connect(self.__on_button)
        shortcut.enter_event_signal().connect(self.__on_button_enter_event)
        body_layout.add_widget(shortcut)

        hide = AppLauncherContextMenuButton(
            text='Hide', icon_name='view-hidden', button_id='hide')
        hide.clicked_signal().connect(self.__on_button)
        hide.enter_event_signal().connect(self.__on_button_enter_event)
        body_layout.add_widget(hide)

    def toggle_pin_button(self) -> None:
        """Toggle pin button.

        Will go from 'pin' to 'unpin'.
        """
        if self.__pin_button.is_visible():
            self.__pin_button.set_visible(False)
            self.__pin_remove_button.set_visible(True)
        else:
            self.__pin_button.set_visible(True)
            self.__pin_remove_button.set_visible(False)

    def pin_button_is_visible(self) -> bool:
        """Whether the favorite button is visible

        Gets a boolean value indicating whether the favorite button is visible.
        """
        return self.__pin_button.is_visible()

    def clicked_signal(self) -> QtCore.Signal:
        """Mouse clicked signal

        Gets the signal that indicates that the mouse clicked on the widget.
        """
        return self.__clicked_signal

    def enter_event_signal(self) -> QtCore.Signal:
        """Mouse hover event

        Gets the signal that is emitted when the mouse hovers over the widget.
        """
        return self.__enter_event_signal

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.

        :param event: QEvent received by sent signal
        """
        # event -> QtGui.QMouseEvent
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def __on_button(self, widget: AppLauncherContextMenuButton) -> None:
        # When app launcher context menu is clicked
        self.__clicked_signal.emit(widget)

    def __on_button_enter_event(
            self, widget: AppLauncherContextMenuButton) -> None:
        # When mouse hovers over app launcher context menu
        self.__enter_event_signal.emit(widget)

    def __str__(self) -> str:
        # String for print() fn
        return ('<AppLauncherContextMenu: '
                f'{self.__desktop_file.content["[Desktop Entry]"]["Name"]}>')


class AppLauncher(QtWidgets.QWidget):
    """App launcher widget

    Displays the application to launch.
    """
    __clicked_signal = QtCore.Signal(object)
    __right_clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)
    __leave_event_signal = QtCore.Signal(object)
    __mount_app_launcher_signal = QtCore.Signal(object)

    def __init__(
            self,
            desktop_file: DesktopFile,
            pin_desktop_file_list: list,
            no_thread: bool = False,
            *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.

        :param desktop_file: DesktopFile object
        :param pin_desktop_file_list: list of pinned DesktopFile objects
        :param no_thread:
            Boolean that indicates if this widget will use
            thread to build itself
        """
        super().__init__(*args, **kwargs)
        self.__desktop_file = desktop_file
        self.__pin_desktop_file_list = pin_desktop_file_list
        self.__no_thread = no_thread
        self.__context_menu_is_visible = False

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

        # Body
        self.__body_container = QtWidgets.QWidget()
        self.__body_container.set_style_sheet(self.__style_sheet)
        self.__main_layout.add_widget(self.__body_container)

        self.__body_layout = QtWidgets.QVBoxLayout()
        self.__body_layout.set_contents_margins(0, 30, 0, 0)
        self.__body_container.set_layout(self.__body_layout)

        # Context
        self.__app_launcher_context_menu = None

        self.__contex_container = QtWidgets.QWidget()
        self.__contex_container.set_visible(False)
        self.__contex_container.set_style_sheet(self.__style_sheet)
        self.__main_layout.add_widget(self.__contex_container)

        self.__context_layout = QtWidgets.QVBoxLayout()
        self.__context_layout.set_contents_margins(0, 0, 0, 0)
        self.__contex_container.set_layout(self.__context_layout)

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
        """Contents of a desktop file

        Gets the contents of a desktop file in the form of an object
        of type DesktopFile.
        """
        return self.__desktop_file

    def app_launcher_context_menu(self) -> AppLauncherContextMenu:
        """Application launcher context menu

        Gets the object which is the application launcher context menu.
        """
        return self.__app_launcher_context_menu

    def context_menu_is_visible(self) -> bool:
        """Whether the context menu is visible

        Gets a boolean value indicating whether the context menu is visible.
        """
        return self.__context_menu_is_visible

    def set_context_menu_to_visible(self, visible: bool) -> None:
        """Configure context menu visibility.

        Pass a boolean value of True to make the context menu visible, or
        pass False to make it invisible.

        :param visible: Boolean value
        """
        if visible:
            if not self.__contex_container.is_visible():
                self.__body_container.set_visible(False)
                self.__contex_container.set_visible(True)
        else:
            if self.__contex_container.is_visible():
                self.__body_container.set_visible(True)
                self.__contex_container.set_visible(False)

    def toggle_pin_button(self) -> None:
        """Toggle pin button.

        Will go from 'pin' to 'unpin'.
        """
        if self.__app_launcher_context_menu:
            self.__app_launcher_context_menu.toggle_pin_button()

    def clicked_signal(self) -> QtCore.Signal:
        """Mouse clicked signal

        Gets the signal that indicates that the mouse clicked on the widget.
        """
        return self.__clicked_signal

    def right_clicked_signal(self) -> QtCore.Signal:
        """Mouse right click signal

        Gets the signal that is emitted when the right mouse button is pressed.
        """
        return self.__right_clicked_signal

    def enter_event_signal(self) -> QtCore.Signal:
        """Mouse hover event

        Gets the signal that is emitted when the mouse hovers over the widget.
        """
        return self.__enter_event_signal

    def leave_event_signal(self) -> QtCore.Signal:
        """Mouse-over event outside the widget

        Gets the signal that is emitted when the mouse leaves the top of
        the widget.
        """
        return self.__leave_event_signal

    def __mount_app_launcher_thread(self) -> None:
        # Wait for the widget to render to assemble the app launcher body
        time.sleep(0.05)
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

        # Context
        self.__app_launcher_context_menu = AppLauncherContextMenu(
            desktop_file=self.__desktop_file,
            pin_desktop_file_list=self.__pin_desktop_file_list)
        self.__app_launcher_context_menu.clicked_signal().connect(
            self.__on_context)
        self.__context_layout.add_widget(self.__app_launcher_context_menu)

        # Accent
        self.__bottom_highlight_line.set_style_sheet(self.__style_sheet)
        self.__bottom_highlight_line.set_fixed_height(5)

    def enter_event(self, event: QtCore.QEvent) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.

        :param event: QEvent received by sent signal
        """

        self.__body_container.set_style_sheet(self.__style_sheet_hover)
        self.__bottom_highlight_line.set_style_sheet(
            'background-color: rgba(255, 255, 255, 0.3);')
        self.__enter_event_signal.emit(self)
        event.ignore()

    def leave_event(self, event: QtCore.QEvent) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.

        :param event: QEvent received by sent signal
        """
        self.__body_container.set_style_sheet(self.__style_sheet)
        self.__bottom_highlight_line.set_style_sheet(self.__style_sheet)
        self.__leave_event_signal.emit(self)
        event.ignore()

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.

        :param event: QEvent received by sent signal
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)
        elif event.button() == QtCore.Qt.RightButton:
            self.__right_clicked_signal.emit(self)

    def paint_event(self, event: QtCore.QEvent) -> None:
        """Drawing event

        Draws a logo of a package installer type.

        :param event: QEvent received by sent signal
        """
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

    def __on_context(self, widget) -> None:
        # Emit a clicked signal
        self.__clicked_signal.emit(widget)

    def __str__(self) -> str:
        # String for print() fn
        return ('<AppLauncher: '
                f'{self.__desktop_file.content["[Desktop Entry]"]["Name"]}>')


class GhostAppLauncher(QtWidgets.QWidget):
    """A bodiless widget

    Made to fill a row space when there are no more valid widgets to use.
    """
    __clicked_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.
        """
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
        """Mouse clicked signal

        Gets the signal that indicates that the mouse clicked on the widget.
        """
        return self.__clicked_signal

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.

        :param event: QEvent received by sent signal
        """
        # event -> QtGui.QMouseEvent
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def __str__(self) -> str:
        # String for print() fn
        return '<GhostAppLauncher: Boo>'


class CategoryButton(QtWidgets.QWidget):
    """Button widget

    A custom button to use for category pagination.
    """
    __clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)

    def __init__(
            self, text: str = None, icon_name: str = None,
            *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.

        :param text: Text that will be displayed on the button
        :param icon_name: Name of the icon that will be displayed on the button
        """
        super().__init__(*args, **kwargs)
        self.set_style_sheet('font-size: 16px;')

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
        self.__text_label = QtWidgets.QLabel(
            self.__text if self.__text else '')
        self.__text_label.set_contents_margins(20, 10, 5, 10)
        self.__text_label.set_style_sheet('background: transparent;')
        self.__text_layout.add_widget(self.__text_label)

        # Accent
        self.__bottom_highlight_line = QtWidgets.QWidget()
        self.__bottom_highlight_line.set_fixed_height(3)
        self.__bottom_highlight_line.set_style_sheet(
            'background: transparent;')
        self.__body_layout.add_widget(self.__bottom_highlight_line)

    def clicked_signal(self) -> QtCore.Signal:
        """Mouse clicked signal

        Gets the signal that indicates that the mouse clicked on the widget.
        """
        return self.__clicked_signal

    def enter_event_signal(self) -> QtCore.Signal:
        """Mouse hover event

        Gets the signal that is emitted when the mouse hovers over the widget.
        """
        return self.__enter_event_signal

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
        """Widget text

        Gets the text used in the widget.
        """
        return self.__text_label.text()

    def set_enter_event_enabled(self, disbled: bool) -> None:
        """Enables the enter event

        Enables or disables the widget's ability to receive or emit enter
        events.

        :param disbled: True or False values
        """
        self.__enter_event_enabled = disbled

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget.

        Emits a signal that the widget has been clicked.

        :param event: QEvent received by sent signal
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def enter_event(self, event: QtCore.QEvent) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.

        :param event: QEvent received by sent signal
        """
        if self.__enter_event_enabled:
            if not self.__state:
                self.__main_container.set_style_sheet("""
                    background-color: rgba(255, 255, 255, 0.05);""")
            self.__clicked_signal.emit(self)
            self.__enter_event_signal.emit(self)
            event.ignore()

    def leave_event(self, event: QtCore.QEvent) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.

        :param event: QEvent received by sent signal
        """
        if self.__enter_event_enabled:
            if not self.__state:
                self.__main_container.set_style_sheet("""
                    background: transparent;""")
            event.ignore()

    def __str__(self) -> str:
        # String for print() fn
        return f'<CategoryButton: {self.__text}>'


class EnergyButton(QtWidgets.QWidget):
    """Button widget

    A custom button to use for category pagination.
    """
    __clicked_signal = QtCore.Signal(object)

    def __init__(
            self,
            icon_name: str, name_id: str = None,
            *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.

        :param icon_name: Name of the icon that will be displayed on the button
        :param name_id: ID set manually
        """
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
        """Name ID

        Gets the identifier of the button that was defined by parameter.
        """
        return self.__name_id

    def icon_name(self) -> str:
        """Icon name

        Gets the name of the icon used in the button.
        """
        return self.__icon_name

    def set_enter_event_enabled(self, disbled: bool) -> None:
        """Enables the enter event

        Enables or disables the widget's ability to receive or emit enter
        events.

        :param disbled: True or False values
        """
        self.__enter_event_enabled = disbled

    def clicked_signal(self) -> QtCore.Signal:
        """Mouse clicked signal

        Gets the signal that indicates that the mouse clicked on the widget.
        """
        return self.__clicked_signal

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget

        Emits a signal that the widget has been clicked.

        :param event: QEvent received by sent signal
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.__clicked_signal.emit(self)

    def enter_event(self, event: QtCore.QEvent) -> None:
        """Mouse hover event

        Highlight colors when mouse hovers over widget.

        :param event: QEvent received by sent signal
        """
        if self.__enter_event_enabled:
            self.__icon_view.set_style_sheet("""
                border-radius: 40px;
                background-color: rgba(255, 255, 255, 0.05);""")
        event.ignore()

    def leave_event(self, event: QtCore.QEvent) -> None:
        """Mouse-over event outside the widget

        Remove highlighting colors when the mouse leaves the widget.

        :param event: QEvent received by sent signal
        """
        if self.__enter_event_enabled:
            self.__icon_view.set_style_sheet('background: transparent;')
        event.ignore()

    def __str__(self) -> str:
        # String for print() fn
        return f'<EnergyButton: {self.__icon_name}>'


class AppGrid(QtWidgets.QScrollArea):
    """App launcher grid widget"""
    __clicked_signal = QtCore.Signal(object)
    __right_clicked_signal = QtCore.Signal(object)
    __enter_event_signal = QtCore.Signal(object)
    __leave_event_signal = QtCore.Signal(object)
    __mount_grid_signal = QtCore.Signal(object)

    def __init__(
            self,
            desktop_file_list: list,
            pin_desktop_file_list: list,
            columns_num: int = 5,
            empty_lines: int = 0,
            *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.

        :param desktop_file_list: DesktopFile objects list
        :param pin_desktop_file_list: Pinned DesktopFile objects list
        :param columns_num: Number of grid columns, default is 5
        :param empty_lines: Number of empty lines, default is 0
        """
        super().__init__(*args, **kwargs)
        self.__desktop_file_list = desktop_file_list
        self.__favorite_desktop_file_list = pin_desktop_file_list
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
        self.__mount_grid_signal.connect(self.__mount_grid)
        mount_grid_thread = threading.Thread(target=self.__mount_grid_thread)
        mount_grid_thread.start()

    def clicked_signal(self) -> QtCore.Signal:
        """Mouse button click signal

        Gets the signal that is emitted when a mouse button is pressed.
        """
        return self.__clicked_signal

    def right_clicked_signal(self) -> QtCore.Signal:
        """Mouse right click signal

        Gets the signal that is emitted when the right mouse button is pressed.
        """
        return self.__right_clicked_signal

    def enter_event_signal(self) -> QtCore.Signal:
        """Mouse hover event

        Gets the signal that is emitted when the mouse hovers over the widget.
        """
        return self.__enter_event_signal

    def leave_event_signal(self) -> QtCore.Signal:
        """Mouse-over event outside the widget

        Gets the signal that is emitted when the mouse leaves the top of
        the widget.
        """
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

            no_thread = False
            if len(self.__desktop_file_list) < 7:
                no_thread = True

            app_launcher = AppLauncher(
                pin_desktop_file_list=self.__favorite_desktop_file_list,
                desktop_file=desktop_file,
                no_thread=no_thread)
            app_launcher.clicked_signal().connect(
                self.__on_app_launcher_clicked_signal)
            app_launcher.right_clicked_signal().connect(
                self.__on_app_launcher_right_clicked_signal)
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

    def __mount_ghost_grid(self) -> None:
        # Mount an empty grid without apps
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

    def __on_app_launcher_clicked_signal(
            self, widget: GhostAppLauncher | AppLauncher) -> None:
        # When the app is clicked, this method is triggered
        self.__clicked_signal.emit(widget)

    def __on_app_launcher_right_clicked_signal(
            self, widget: GhostAppLauncher | AppLauncher) -> None:
        # When the app is clicked, this method is triggered
        self.__right_clicked_signal.emit(widget)

    def __on_launcher_enter_event_signal(self, widget: AppLauncher) -> None:
        # Emits a signal when the mouse hovers over the widget
        self.enter_event_signal().emit(widget)

    def __on_launcher_leave_event_signal(self, widget: AppLauncher) -> None:
        # Emits a signal when the mouse moves away from the widget
        self.leave_event_signal().emit(widget)

    def __str__(self) -> str:
        # String for print() fn
        return f'<AppGrid: {id(self)}>'


class SearchApps(QtWidgets.QLineEdit):
    """A QLineEdit custom widget"""
    __text_changed = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes.
        """
        super().__init__(*args, **kwargs)
        self.set_style_sheet("""
            color: #AAA;
            font-size: 20px;
            background: transparent;
            border: 0px;
            padding: 10px;""")
        self.textChanged.connect(lambda text: self.__text_changed.emit(text))

    def text_changed_signal(self) -> QtCore.Signal:
        """Text changed signal

        Gets the signal when the text changes.
        """
        return self.__text_changed

    def mouse_press_event(self, event: QtCore.QEvent) -> None:
        """Mouse click event on the widget

        Tracks and handles when any mouse button is pressed.

        :param event: QEvent received by sent signal
        """
        if (event.button() == QtCore.Qt.LeftButton
                or event.button() == QtCore.Qt.RightButton):
            print(self)

    def __str__(self) -> str:
        # String for print() fn
        return f'<SearchApps: {id(self)}>'


class ElidedLabel(QtWidgets.QLabel):
    """A label widget that can display only the necessary text

    Hidden text is converted to an ellipsis.
    """
    def paint_event(self, event: QtCore.QEvent) -> None:
        """Event that draws the text

        Calculate the size of the text that can be displayed and convert
        the rest to an ellipsis.

        :param event: QEvent received by sent signal
        """
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elided_text(
            self.text(), QtCore.Qt.ElideRight, self.width())
        painter.draw_text(self.rect(), self.alignment(), elided)
        event.ignore()

    def __str__(self) -> str:
        # String for print() fn
        return f'<ElidedLabel: {id(self)}>'
