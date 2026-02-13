import os
import json
from pathlib import Path
import easygui
import globals

class ImportSchedule:
    def __init__(self):
        pass

    def get_schedule_file(self):
        """Select the schedule file to import"""

        # Set the directory to open in the dialog box to the default directory where schedules are saved .../Documents/ScheduleTimer Export
        default_dir = globals.get_default_save_dir() / " "

        # If the default directory does not exist, set the directory to open to the Documents directory
        if not Path.exists(default_dir):
            default_dir = globals.DOCUMENTS_DIR / " "

        file_path = easygui.fileopenbox(title="Select schedule to import", default=default_dir)

        return file_path

    def get_schedule_data(self):
        """Extract the contents of schedule file"""

        file_path = self.get_schedule_file()

        with open(file_path, "r") as schedule_file:
            # data = json.load(schedule_file)
            # print (data)
            data = ""
        return data

    def is_valid_file(self) -> bool:
        """Authenticate the schedule file"""
        file_path = self.get_schedule_file()

        # Validate that the file is a JSON file
        if file_path.endswith(".json"):
            print("File is a valid JSON file")
        else:
            print("File is not a valid JSON file")

        schedule_data = self.get_schedule_data()

        try:
            for data in schedule_data:
                session_title = data["Session Title"]
                minutes = data["Minutes"]
                seconds = data["Seconds"]
        except KeyError:
            return False
            print("Invalid schedule file")
        else:
            return True