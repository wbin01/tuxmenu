#!/usr/bin/env python3
# Reference:
#   www.freedesktop.org/wiki/Specifications/
#   www.freedesktop.org/wiki/Specifications/basedir-spec/
#   www.freedesktop.org/wiki/Specifications/desktop-entry-spec/
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
                if 'applications' in os.listdir(data_dir):
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
        self.__as_dict = None

    @property
    def as_dict(self) -> dict:
        """Contents of a desktop file as a dictionary

        Example:
        >>> desktop_file = DesktopFile(
        ...     url='/usr/share/applications/firefox.desktop')
        >>> desktop_file.as_dict['[Desktop Entry]']['Name']
        'Firefox Web Browser'
        >>> desktop_file.as_dict['[Desktop Entry]']['Type']
        'Application'
        >>> for key in desktop_file.as_dict.keys():
        ...     print(key)
        ...
        [Desktop Entry]
        [Desktop Action new-window]
        [Desktop Action new-private-window]
        >>>
        >>> desktop_file.as_dict['[Desktop Action new-window]']['Name']
        'Open a New Window'
        """
        if not self.__as_dict:
            self.__parse_file_to_dict()
        return self.__as_dict

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
                re.findall('\[[A-Z]', desktop_file_line),
                re.split('\[[A-Z]', desktop_file_line)[1:])]

        # Create dict
        self.__as_dict = {}
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

            self.__as_dict[escope_header] = escope_keys_and_values

    def __gt__(self, other) -> bool:
        if '[Desktop Entry]' in self.__as_dict:
            return self.__as_dict['[Desktop Entry]']['Name'] > other
        return self.__url > other

    def __lt__(self, other) -> bool:
        if '[Desktop Entry]' in self.__as_dict:
            return self.__as_dict['[Desktop Entry]']['Name'] < other
        return self.__url < other

    def __eq__(self, other) -> bool:
        if '[Desktop Entry]' in self.__as_dict:
            return self.__as_dict['[Desktop Entry]']['Name'] == other
        return self.__url == other

    def __ge__(self, other) -> bool:
        if '[Desktop Entry]' in self.__as_dict:
            return self.__as_dict['[Desktop Entry]']['Name'] >= other
        return self.__url >= other

    def __le__(self, other) -> bool:
        if '[Desktop Entry]' in self.__as_dict:
            return self.__as_dict['[Desktop Entry]']['Name'] <= other
        return self.__url <= other

    def __ne__(self, other) -> bool:
        if '[Desktop Entry]' in self.__as_dict:
            return self.__as_dict['[Desktop Entry]']['Name'] != other
        return self.__url != other

    def __str__(self) -> str:
        if '[Desktop Entry]' in self.__as_dict:
            return f'<DesktopFile: {self.as_dict["[Desktop Entry]"]["Name"]}>'
        return f'<DesktopFile: {self.__url.split("/")[-1]}>'


class MenuSchema(object):
    """Template to build the menu."""
    def __init__(self) -> None:
        """Class constructor

        Initialize class properties.
        """
        # https://specifications.freedesktop.org/
        # menu-spec/menu-spec-1.0.html#category-registry
        self.__as_dict = {
            'All': [], 'Development': [], 'Multimedia': [], 'Education': [],
            'Game': [], 'Graphics': [], 'Network': [], 'Office': [],
            'Settings': [], 'System': [], 'Utility': [], 'Others': []}
        self.update_menu()

    @property
    def as_dict(self) -> dict:
        """Menu template as a dict

        A dictionary where the keys (str) are the menu categories, and the
        values are the applications (DesktoFile) displayed in the category.
        """
        return self.__as_dict

    def update_menu(self) -> None:
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

            if '[Desktop Entry]' not in desktop_file.as_dict:
                desktop_file_is_valid = False
            else:
                desktop_entry = desktop_file.as_dict['[Desktop Entry]']

                if desktop_entry['Type'] != 'Application':
                    desktop_file_is_valid = False
                if ('NoDisplay' in desktop_entry and
                        desktop_entry['NoDisplay'] == 'true'):
                    desktop_file_is_valid = False
                if ('Hidden' in desktop_entry and
                        desktop_entry['Hidden'] == 'true'):
                    desktop_file_is_valid = False
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
                desktop_item = desktop_file
                # (
                # desktop_file.as_dict['[Desktop Entry]']['Name'],
                # desktop_file)

                # Categ 'All'
                self.__as_dict['All'].append(desktop_item)

                # Categ 'Others'
                if 'Categories' not in desktop_entry:
                    self.__as_dict['Others'].append(desktop_item)
                    continue

                # Remaining categories
                for categ in self.__as_dict:
                    if categ in desktop_entry['Categories'].split(';'):
                        self.__as_dict[categ].append(desktop_item)

            # for item in self.__as_dict:
            #     la = [x.as_dict['Name'] for x in self.__as_dict[item]]


if __name__ == '__main__':
    import locale
    m = MenuSchema()
    for cat, apps in m.as_dict.items():
        print(f'{cat}: {len(apps)}')
        if apps:
            apps.sort()
            for i in apps:
                print('\t', i)
        # appz = []
        # for a in apps:
        #     gen_local = f'GenericName[{locale.getdefaultlocale()[0]}]'
        #     if gen_local in a.as_dict["[Desktop Entry]"]:
        #         item = a.as_dict["[Desktop Entry]"][gen_local]
        #         appz.append((item.lower(), item))
        #     elif 'GenericName' in a.as_dict["[Desktop Entry]"]:
        #         item = a.as_dict["[Desktop Entry]"]['GenericName']
        #         appz.append((item.lower(), item))
        #     else:
        #         item = a.as_dict["[Desktop Entry]"]['Name']
        #         appz.append((item.lower(), item))
        print()
