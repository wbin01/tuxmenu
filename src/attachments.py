#!/usr/bin/env python3
# Reference:
#   www.freedesktop.org/wiki/Specifications/
#   www.freedesktop.org/wiki/Specifications/basedir-spec/
#   www.freedesktop.org/wiki/Specifications/desktop-entry-spec/
import json
import os
import re
import subprocess
from subprocess import getoutput


class DesktopFileLocations(object):
    """Desktop files location object.

    Locate system desktop entry file paths.
    Files that contain the '.desktop' extension and are used internally by
    menus to find applications.

    Follows the specification from freedesktop.org:
        www.freedesktop.org/wiki/Specifications/basedir-spec/
    """
    def __init__(self) -> None:
        """Class constructor

        Initialize class properties.
        """
        self.__file_dirs = self.__find_dirs()
        self.__ulrs_by_priority = None
        self.__ulrs = None

    @property
    def file_dirs(self) -> list:
        """All desktop files path

        String list of all desktop file paths on the system as per settings
        in $XDG_DATA_HOME and $XDG_DATA_DIRS of the freedesktop.org spec.
        """
        return self.__file_dirs

    @property
    def ulrs_by_priority(self) -> list:
        """Desktop files ulrs (/path/file.desktop)

        String list of all desktop file URLs in order of priority.
        If there are files with the same name, then user files in "~/.local/",
        will have priority over system files. Likewise, files in
        "/usr/local/share" take precedence over files in "/usr/share".
        """
        if not self.__ulrs_by_priority:
            self.__ulrs_by_priority = (
                self.__find_urls_by_priority())
        return self.__ulrs_by_priority

    @property
    def ulrs(self) -> list:
        """All desktop files ulrs (/path/file.desktop)

        String list of all desktop file URLs. It may contain files with the
        same name in different paths. To get valid single files, use
        "ulrs_by_priority" property.
        """
        if not self.__ulrs:
            self.__ulrs = (
                self.__find_urls())
        return self.__ulrs

    @staticmethod
    def __find_dirs() -> list:
        xdg_data_home = getoutput('echo $XDG_DATA_HOME')
        xdg_data_home = (
            os.path.join(xdg_data_home, 'applications') if xdg_data_home else
            os.path.join(os.environ['HOME'], '.local/share/applications'))

        desktop_file_dirs = [xdg_data_home]

        xdg_data_dirs = getoutput('echo $XDG_DATA_DIRS')
        if xdg_data_dirs:
            for data_dir in xdg_data_dirs.split(':'):
                if os.path.isdir(data_dir) and 'applications' in os.listdir(data_dir):
                    desktop_file_dirs.append(
                        os.path.join(data_dir, 'applications'))
        else:
            desktop_file_dirs += [
                '/usr/local/share/applications', '/usr/share/applications']

        return desktop_file_dirs

    def __find_urls_by_priority(self) -> list:
        # Get url in order of precedence

        checked_file_names = []
        desktop_files = []
        for desktop_dir in self.__file_dirs:
            for desktop_file in os.listdir(desktop_dir):

                if desktop_file not in checked_file_names:
                    checked_file_names.append(desktop_file)

                    if ('~' not in desktop_file
                            and desktop_file.endswith('.desktop')):
                        desktop_files.append(
                            os.path.join(desktop_dir, desktop_file))

        return desktop_files

    def __find_urls(self) -> list:
        # Get all url
        desktop_files = []
        for desktop_dir in self.__file_dirs:
            for desktop_file in os.listdir(desktop_dir):
                if ('~' not in desktop_file
                        and desktop_file.endswith('.desktop')):
                    desktop_files.append(
                        os.path.join(desktop_dir, desktop_file))

        return desktop_files

    def __str__(self) -> str:
        return f'<DesktopFileLocations: {id(self)}>'


class DesktopFile(object):
    """Desktop files object.

    Desktop files are files with the extension '.desktop' and are used
    internally by menus to find applications. This object converts these files
    into a dictionary to provide easy access to their values.
    """
    def __init__(self, url: str) -> None:
        """Class constructor

        Initialize class properties.

        :param url:
            String from a desktop file like: "/path/file.desktop"
        """
        self.__url = os.path.abspath(url)
        self.__content = None

    @property
    def content(self) -> dict:
        """Contents of a desktop file as a dictionary

        Example:
        >>> desktop_file = DesktopFile(
        ...     url='/usr/share/applications/firefox.desktop')
        >>> desktop_file.content['[Desktop Entry]']['Name']
        'Firefox Web Browser'
        >>> desktop_file.content['[Desktop Entry]']['Type']
        'Application'
        >>> for key in desktop_file.content.keys():
        ...     print(key)
        ...
        [Desktop Entry]
        [Desktop Action new-window]
        [Desktop Action new-private-window]
        >>>
        >>> desktop_file.content['[Desktop Action new-window]']['Name']
        'Open a New Window'
        """
        if not self.__content:
            self.__parse_file_to_dict()
        return self.__content

    @property
    def url(self) -> str:
        """URL of the desktop file

        The URL used to construct this object, like: "/path/file.desktop".

        :return: String from a desktop file
        """
        return self.__url

    def __parse_file_to_dict(self) -> None:
        # Open file
        with open(self.__url, 'r') as desktop_file:
            desktop_file_line = desktop_file.read()

        # Separate scope: "[header]key=value...", "[h]k=v...",
        desktop_scope = [
            x + y for x, y in zip(
                re.findall(r'\[[A-Z]', desktop_file_line),
                re.split(r'\[[A-Z]', desktop_file_line)[1:])]

        # Create dict
        self.__content = {}
        for scope in desktop_scope:
            escope_header = ''           # [Desktop Entry]
            escope_keys_and_values = {}  # Key=Value

            for index_num, scopeline in enumerate(scope.split('\n')):
                if index_num == 0:
                    escope_header = scopeline
                else:
                    if scopeline and scopeline[0] != '#' and '=' in scopeline:
                        line_key, line_value = scopeline.split('=', 1)
                        escope_keys_and_values[line_key] = line_value

            self.__content[escope_header] = escope_keys_and_values

    def __gt__(self, obj) -> bool:
        if '[Desktop Entry]' in self.content:
            return self.content['[Desktop Entry]']['Name'].lower() > obj
        return self.url > obj

    def __lt__(self, obj) -> bool:
        if '[Desktop Entry]' in self.content:
            return self.content['[Desktop Entry]']['Name'].lower() < obj
        return self.url < obj

    def __eq__(self, obj) -> bool:
        if '[Desktop Entry]' in self.content:
            return self.content['[Desktop Entry]']['Name'].lower() == obj
        return self.url == obj

    def __ge__(self, obj) -> bool:
        if '[Desktop Entry]' in self.content:
            return self.content['[Desktop Entry]']['Name'].lower() >= obj
        return self.url >= obj

    def __le__(self, obj) -> bool:
        if '[Desktop Entry]' in self.content:
            return self.content['[Desktop Entry]']['Name'].lower() <= obj
        return self.url <= obj

    def __ne__(self, obj) -> bool:
        if '[Desktop Entry]' in self.content:
            return self.content['[Desktop Entry]']['Name'].lower() != obj
        return self.url != obj

    def __str__(self) -> str:
        if '[Desktop Entry]' in self.content:
            return f'<DesktopFile: {self.content["[Desktop Entry]"]["Name"]}>'
        return f'<DesktopFile: {self.url.split("/")[-1]}>'


class MenuSchema(object):
    """Template to build the menu."""
    def __init__(self) -> None:
        """Class constructor

        Initialize class properties.
        """
        # https://specifications.freedesktop.org/
        # menu-spec/menu-spec-1.0.html#category-registry
        self.__schema = {
            'Home': [], 'All': [], 'Development': [], 'Education': [],
            'Multimedia': [], 'AudioVideo': [], 'Audio': [], 'Video': [],
            'Game': [], 'Graphics': [], 'Network': [], 'Office': [],
            'Settings': [], 'System': [], 'Utility': [], 'Others': [],
            'AppImage': [], 'Snap': [], 'Flatpak': []}
        self.__icons_schema = {
            'Home': 'applications-all', 'All': 'applications-all',
            'Development': 'applications-development',
            'Education': 'applications-education',
            'Multimedia': 'applications-multimedia',
            'AudioVideo': 'applications-other', 'Audio': 'applications-other',
            'Video': 'applications-other', 'Game': 'applications-games.svg',
            'Graphics': 'applications-graphics',
            'Network': 'applications-network', 'Office': 'applications-office',
            'Settings': 'preferences', 'System': 'applications-system',
            'Utility': 'applications-utilities', 'Others':'applications-other',
            'AppImage': 'application-vnd.appimage.svg',
            'Snap': 'application-vnd.snap',
            'Flatpak': 'application-vnd.flatpak.ref.svg'
        }
        self.update_schema()

    @property
    def icons_schema(self) -> dict:
        """Icon name schema

        Best system icon name for each category
        """
        return self.__icons_schema

    @property
    def schema(self) -> dict:
        """Menu template as a dict

        A dictionary where the keys (str) are the menu categories, and the
        values are the applications (DesktoFile) displayed in the category.
        """
        return self.__schema

    def update_schema(self) -> None:
        """Update menu schema

        Update "as_dict" property.
        """
        # percorrer urls
        desktop_file_locations = DesktopFileLocations()
        for desktop_file_url in desktop_file_locations.ulrs_by_priority:
            # Get a file and check if it is a valid file
            desk_env = subprocess.getoutput('echo $XDG_CURRENT_DESKTOP')
            desktop_file = DesktopFile(url=desktop_file_url)
            desktop_file_is_valid = True
            desktop_entry = None

            if '[Desktop Entry]' not in desktop_file.content:
                desktop_file_is_valid = False
            else:
                desktop_entry = desktop_file.content['[Desktop Entry]']

                if desktop_entry['Type'] != 'Application':
                    desktop_file_is_valid = False
                elif ('NoDisplay' in desktop_entry and
                        desktop_entry['NoDisplay'] == 'true'):
                    desktop_file_is_valid = False
                elif ('Hidden' in desktop_entry and
                        desktop_entry['Hidden'] == 'true'):
                    desktop_file_is_valid = False
                else:
                    if 'OnlyShowIn' in desktop_entry:
                        desktop_file_is_valid = False
                        if desk_env in desktop_entry['OnlyShowIn'].split(';'):
                            desktop_file_is_valid = True

                    if 'NotShowIn' in desktop_entry:
                        desktop_file_is_valid = True
                        if desk_env in desktop_entry['NotShowIn'].split(';'):
                            desktop_file_is_valid = False

            # Check categories and save in correct category
            if desktop_file_is_valid:
                # Categ 'All'
                self.__schema['All'].append(desktop_file)

                # Categ 'Others'
                if 'Categories' not in desktop_entry:
                    self.__schema['Others'].append(desktop_file)
                    continue

                # Remaining categories
                for categ in self.__schema:
                    if categ in desktop_entry['Categories'].split(';'):
                        # Convert 'Audio' and 'Video' for 'Multimedia'
                        if (categ == 'AudioVideo' or
                                categ == 'Audio' or categ == 'Video'):
                            categ = 'Multimedia'
                            if desktop_file not in self.__schema[categ]:
                                self.__schema[categ].append(desktop_file)
                        else:
                            self.__schema[categ].append(desktop_file)

                if '/snap/bin/' in desktop_entry['Exec']:
                    self.__schema['Snap'].append(desktop_file)
                elif '/usr/bin/flatpak' in desktop_entry['Exec']:
                    self.__schema['Flatpak'].append(desktop_file)
                # APPIMAGE_EXTRACT_AND_RUN=1 /opt/Telegram/Telegram
                elif ('AppImage' in desktop_entry['Exec'] or
                        'Telegram' in desktop_entry['Exec']):
                    self.__schema['AppImage'].append(desktop_file)

    def __str__(self) -> str:
        return f'<MenuSchema: {id(self)}>'


class EnergyButtonsSchema(object):
    """Template to build the energy buttons."""
    def __init__(self) -> None:
        """Class constructor

        Initialize class properties.
        """
        self.__schema = {
            'lock-screen': {
                'text': 'Lock screen',
                'icon-name': 'system-lock-screen',  # loginctl unlock-session
                'command': ['loginctl', 'lock-session']},
            'suspend': {
                # qdbus6 org.kde.Shutdown /Shutdown suspend
                'text': 'Suspend',
                'icon-name': 'system-suspend',
                'command': ['systemctl', 'suspend']},  # systemctl hibernate
            'reboot': {
                # qdbus6 org.kde.Shutdown /Shutdown reboot
                'text': 'Reboot',
                'icon-name': 'system-reboot',
                'command': ['systemctl', 'reboot']},
            'shutdown': {
                # qdbus6 org.kde.Shutdown /Shutdown powerOff
                'text': 'Shutdown',
                'icon-name': 'system-shutdown',
                'command': ['systemctl', 'poweroff']},
            'log-out': {
                # loginctl terminate-user $USER
                # loginctl terminate-session $XDG_SESSION_ID
                
                # qdbus org.kde.Shutdown /Shutdown logout
                # qdbus6 org.kde.Shutdown /Shutdown logout
                # gnome-session-quit --logout --no-prompt
                # xfce4-session-logout --logout
                # lxqt-leave --logout
                'text': 'Log-out',
                'icon-name': 'system-log-out',
                'command': [
                    'qdbus', 'org.kde.Shutdown', '/Shutdown', 'logout']},
            'switch-user': {
                # loginctl switch-user <user>
                # qdbus org.kde.SDDM /org/kde/SDDM/Greeter callLogin

                # qdbus org.kde.ksmserver /KSMServer logout -1 -1 2
                # qdbus6 org.kde.Shutdown /Shutdown switchUser

                # qdbus6 org.kde.SDDM /org/kde/SDDM DisplaySwitchUser
                # qdbus6 org.freedesktop.DBus / org.freedesktop.DBus.StartServiceByName org.kde.sddm 0
                # qdbus6 org.freedesktop.DBus / org.freedesktop.DBus.StartServiceByName org.kde.sddm 0
                # dm-tool switch-to-greeter
                'text': 'Switch user',
                'icon-name': 'system-switch-user',
                'command': None}}

    @property
    def schema(self) -> dict:
        """Energy buttons template as a dict

        A dictionary that contains the button id as keys. each item stores
        a dictionary with the name of the icon and the command.
        """
        return self.__schema


class SavedApps(object):
    """Configure saved apps"""
    def __init__(self, config_name: str):
        """Class constructor

        Initialize class properties.

        :param config_name: Name that will serve as an ID for the configuration
        """
        self.__config_name = config_name
        self.__config_dirname = 'tuxmenu'
        self.__config_filename = self.__config_name + '.json'

        self.__config_dir_path = (
            os.path.join(os.environ['HOME'], '.config', self.__config_dirname))

        self.__config_file_path = (
            os.path.join(
                self.__config_dir_path,
                self.__config_filename))

        self.__apps = self.__load_apps()

    @property
    def config_name(self) -> str:
        """Config name

        Get the configuration ID name.
        """
        return self.__config_name

    @property
    def apps(self) -> list:
        """Saved apps

        Gets a list of 'DesktopFile' objects from applications that
        have been saved.
        """
        return self.__apps

    @apps.setter
    def apps(self, app_list: list) -> None:
        self.__apps = app_list

    def __load_apps(self) -> list:
        # Read and load config
        if not os.path.isdir(self.__config_dir_path):
            os.makedirs(self.__config_dir_path)

        if not os.path.isfile(self.__config_file_path):
            return []

        with open(self.__config_file_path, 'r') as f:
            json_data = json.load(f)

        urls = []
        if json_data[self.__config_name]:
            for url in json_data[self.__config_name]:
                if os.path.isfile(url):
                    urls.append(DesktopFile(url=url))

        return urls

    def save_apps(self, url_list_apps: list) -> None:
        """Save the apps

        Save apps from list in settings.
        """
        with open(self.__config_file_path, 'w') as f:
            json.dump({self.__config_name: url_list_apps}, f)

    def __str__(self) -> str:
        return f'<SavedApps: {self.__config_name}>'
