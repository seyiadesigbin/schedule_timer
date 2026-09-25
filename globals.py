# This file contains all variables and functions that are used across multiple modules.

from pathlib import Path
import os

PARENT_DIR = Path(__file__).parent.resolve()  # Get the directory the program is running from.
RESOURCES_DIR = Path(PARENT_DIR / "resources")
STYLESHEET_DIR = Path(RESOURCES_DIR / "stylesheets")
ICONS_DIR = Path(RESOURCES_DIR / "icons")
FONTS_DIR = Path(RESOURCES_DIR / "fonts")
APP_FONT_FAMILY = "Barlow"  # Bundled in the fonts directory, so it does not need to be installed on the system
APP_TITLE = "ScheduleTimer- Beta Version"
APP_VERSION = "v1.0"

DOCUMENTS_DIR = Path.home()/"Documents"


# Icons
APP_ICON_DIR = str(Path(ICONS_DIR/"app_icon.png"))
ADD_ICON_DIR = str(Path(ICONS_DIR/"add.png"))
IMPORT_ICON_DIR = str(Path(ICONS_DIR/"import.png"))
EXPORT_ICON_DIR = str(Path(ICONS_DIR/"export.png"))
HELP_ICON_DIR = str(Path(ICONS_DIR/"help.png"))
INFO_ICON_DIR = str(Path(ICONS_DIR/"info.png"))
RESET_ICON_DIR = str(Path(ICONS_DIR/"reset_yellow.png"))
START_ICON_DIR = str(Path(ICONS_DIR/"play.png"))
DELETE_ICON_DIR = str(Path(ICONS_DIR/"delete.png"))
CLOCK_WHITE_ICON_DIR = str(Path(ICONS_DIR/"clock_white.png"))
CLOCK_GREEN_ICON_DIR = str(Path(ICONS_DIR/"clock_green.png"))
CLOCK_RED_ICON_DIR = str(Path(ICONS_DIR/"clock_red.png"))
PAUSE_ICON_DIR = str(Path(ICONS_DIR/"pause.png"))
RESUME_ICON_DIR = str(Path(ICONS_DIR/"resume.png"))
SHOW_ICON_DIR = str(Path(ICONS_DIR/"show_blue.png"))
HIDE_ICON_DIR = str(Path(ICONS_DIR/"hide_blue.png"))
CLOSE_ICON_DIR = str(Path(ICONS_DIR/"close.png"))
GITHUB_ICON_DIR = str(Path(ICONS_DIR/"github.png"))
LINKEDIN_ICON_DIR = str(Path(ICONS_DIR/"linkedin.png"))
WHATSAPP_ICON_DIR = str(Path(ICONS_DIR/"whatsapp.png"))
CREDITS_ICON_DIR = str(Path(ICONS_DIR/"credits.png"))

CREDITS_WEBPAGE_DIR = Path(RESOURCES_DIR / "credits.html")  # Directory for the credits.html file


def load_stylesheet(stylesheet_file_name) -> str:
    """Extracts a qss stylesheet from a specified directory

    :parameter stylesheet_file_name: The stylesheet's file name
    :type stylesheet_file_name: str

    :returns: The extracted stylesheet
    :rtype: str

    """

    file_dir = Path(STYLESHEET_DIR / stylesheet_file_name)  # Get the directory of the stylesheet file

    with open(file_dir, mode="r") as stylesheet_file:
        stylesheet = stylesheet_file.read()
        return stylesheet


def load_fonts():
    """Registers the bundled font files with the application, so they can be used by name in stylesheets

    Must be called after the QApplication is created

    """

    from PySide6.QtGui import QFontDatabase

    for font_file in FONTS_DIR.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))

def get_default_save_dir():
    """Returns the path to the user's documents directory"""

    return DOCUMENTS_DIR/"ScheduleTimer Exports"


# ADD_ICON_DIR = "resources/icons/add.png"
# HELP_ICON_DIR = "resources/icons/help.png"
# INFO_ICON_DIR = "resources/icons/info.png"
# RESET_ICON_DIR = "resources/icons/reset_yellow.png"
# START_ICON_DIR = "resources/icons/play.png"
# DELETE_ICON_DIR = "resources/icons/delete.png"
# CLOCK_WHITE_ICON_DIR = "resources/icons/clock_white.png"
# CLOCK_GREEN_ICON_DIR = "resources/icons/clock_green.png"
# CLOCK_RED_ICON_DIR = "resources/icons/clock_red.png"
# PAUSE_ICON_DIR = "resources/icons/pause.png"
# RESUME_ICON_DIR = "resources/icons/resume.png"
# SHOW_ICON_DIR = "resources/icons/show_blue.png"
# HIDE_ICON_DIR = "resources/icons/hide_blue.png"
# CLOSE_ICON_DIR = "resources/icons/close.png"
# GITHUB_ICON_DIR = "resources/icons/github.png"
# LINKEDIN_ICON_DIR = "resources/icons/linkedin.png"
# WHATSAPP_ICON_DIR = "resources/icons/whatsapp.png"
# CREDITS_ICON_DIR = "resources/icons/credits.png"
