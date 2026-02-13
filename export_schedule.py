# from schedule_item_interface import ScheduleItem
import json
from datetime import datetime
from pathlib import Path
import os
from sqlite3.dbapi2 import Date

import globals


class ExportSchedule:
    def __init__(self, schedule_items):

        self.schedule_list = {}
        self.schedule_items = schedule_items
        self.default_save_dir = self.get_default_save_dir()

        print(self.default_save_dir)

    def extract_schedule_info(self):
        """ Extracts the title and time value of each item in the schedule list"""

        items_count = 0

        for schedule_item in self.schedule_items:
            items_count += 1

            session_title = schedule_item.get_session_title()
            minutes = schedule_item.get_minutes()
            seconds = schedule_item.get_seconds()

            self.schedule_list[items_count] = {
                'Session Title': session_title,
                'Minutes': minutes,
                'Seconds': seconds,
            }

        # print(self.schedule_list)


    def export_schedule_data(self):
        """Exports the data of the schedule list to the JSON file"""

        self.extract_schedule_info()

        # Generate the export file name
        # Format is: Day-YYYY-MM-DD [HH:MM AM/PM]- Schedule.sch

        file_name = datetime.today().strftime('%A, %b-%d-%Y [%H-%M-%S %p]- Schedule.sch')
        # file_name = datetime.today().strftime('%H%M%S %p Schedule.sch')

        # print (file_name)

        # file_name = 'schedule.sch'
        file_path = self.default_save_dir / file_name

        # Open JSON file to export data to
        with open(file_path, mode="w") as schedule_export_file:
            json.dump(self.schedule_list, schedule_export_file, indent=4)



    def get_default_save_dir(self):
        """Returns the default directory to save the schedule

        Default director is: ...User/Documents/ScheduleTimer Exports

        """

        default_save_dir = globals.get_default_save_dir()

        # Create the default directory if it does not exist
        if not Path.exists(default_save_dir):
            os.mkdir(default_save_dir)

        return default_save_dir

        # print(default_save_dir)


# export_schedule = ExportSchedule()