dirs = """ADD_ICON_DIR = "resources/icons/add.png"
HELP_ICON_DIR = "resources/icons/help.png"
INFO_ICON_DIR = "resources/icons/info.png"
RESET_ICON_DIR = "resources/icons/reset_yellow.png"
START_ICON_DIR = "resources/icons/play.png"
DELETE_ICON_DIR = "resources/icons/delete.png"
CLOCK_WHITE_ICON_DIR = "resources/icons/clock_white.png"
CLOCK_GREEN_ICON_DIR = "resources/icons/clock_green.png"
CLOCK_RED_ICON_DIR = "resources/icons/clock_red.png"
PAUSE_ICON_DIR = "resources/icons/pause.png"
RESUME_ICON_DIR = "resources/icons/resume.png"
SHOW_ICON_DIR = "resources/icons/show_blue.png"
HIDE_ICON_DIR = "resources/icons/hide_blue.png"
CLOSE_ICON_DIR = "resources/icons/close.png"
GITHUB_ICON_DIR = "resources/icons/github.png"
LINKEDIN_ICON_DIR = "resources/icons/linkedin.png"
WHATSAPP_ICON_DIR = "resources/icons/whatsapp.png"
CREDITS_ICON_DIR = "resources/icons/credits.png" """.splitlines()

for directory in dirs:
    split = directory.split("=")
    file_name = split[1].rsplit("/")[2].replace('"',"")

    new_dir = f'str(Path(ICONS_DIR/"{file_name}"))'

    print(f"{split[0]}= {new_dir}")

