import datetime, json, os
from typing import List

from config import settings
from api.bamboohr import BambooHR
from api.digitalocean import DigitalOcean
from utils import dates
from utils import ical


class BhrTeamCal:
    """ Class for generating an iCal calendar file for a specific team's time offs in BambooHR."""

    def __init__(self, timeoffs_group, root_path=None):
        """
            Initialize the class with the chosen time offs group
            and (optional) path to the root folder
        """
        config_dir = os.path.dirname(os.path.abspath(__file__))
        settings.load_config(timeoffs_group, config_dir)

        self.bhr = BambooHR(settings.config['BAMBOOHR_KEY'], settings.config['BAMBOOHR_DOMAIN'])

        self.timeoffs_group = timeoffs_group
        self.main_root_path = root_path
        self.team_employees = {}


    def get_whos_out_data(self, from_date, to_date):
        """
            Get data from BambooHR's *Time Off - Who's Out* API report
        """
        data = self.bhr.get_whos_out(from_date, to_date)
        print(f" 1. Whosout acquired. Len={len(data)}, firstID={data[0]['id']}, firstEID={data[0]['employeeId']}")
        return data

    def get_team_employees(self):
        """
            Get custom report from BambooHR which defines the team's employees
        """
        report_data = self.bhr.get_custom_report(settings.config['BAMBOOHR_TEAM_REPORT_ID'])
        print(f" 2. Team report acquired. Len={len(json.dumps(report_data))}")

        name_template = settings.config['BAMBOOHR_NAME_TEMPLATE']
        self.team_employees = {
            int(row['id']): name_template.format(**row)
            for row in report_data['employees']
        }

    def filter_timeoff_requests(self, whos_out_data) -> List[ical.TimeoffData]:
        """
            Prepare daily time off data based on requests' details.

            For each time off record from Who's Out report:
            - Check if the employee is in the team ("eligible")
            - Get the details of time off request by calling BambooHR API
            -- check if the time off's type is in the required group and is approved
            -- prepare event data for each date from TO request, where status==1 (day taken)
        """
        filtered_data = []
        last_date = 'unknown'
        print(" 3. Acquiring requests:")
        eligible_timeoff_types = [int(x) for x in settings.config['TO_TYPES'].split(',')]

        for time_off in whos_out_data:

            employee_id = time_off.get('employeeId')
            if not employee_id or employee_id not in self.team_employees:
                continue

            time_off_request = self.bhr.check_time_off_request(time_off['id'], eligible_timeoff_types)
            print(f"    got request id={time_off['id']},"
                  f" {'ELIGIBLE' if time_off_request else 'not eligible'}" )
            if not time_off_request:
                continue

            for date, status in time_off_request['dates'].items():

                if status == '1': # this means day's taken as time off, not 0
                    employee_display_name = self.team_employees[employee_id]
                    timeoff_req_typename = time_off_request['type']['name']
                    filtered_data.append({
                        'date': datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                        'description': f"{employee_display_name} ({timeoff_req_typename})",
                        'time_off_id': time_off['id']
                    })
                    last_date = date

        print(f"   Done. Last date added: {last_date}.")
        return filtered_data

    def upload_to_spaces(self, ical_file_data):
        """
            Upload file to Digital Ocean Spaces or AWS S3.
            Access parameters are defined in .env file,
            and file path is defined in config.yml
        """
        print(" 5. Uploading iCal file to DO Spaces..")
        do = DigitalOcean(
            spaces_key=settings.config['DO_SPACES_KEY'],
            spaces_secret=settings.config['DO_SPACES_SECRET'],
            spaces_region=settings.config['DO_SPACES_REGION'],
            spaces_bucket=settings.config['DO_SPACES_BUCKET'],
            spaces_path=settings.config['DO_SPACES_PATH']
        )
        do.upload_to_spaces(ical_file_data)
        print("    Successfully uploaded to ", settings.config['DO_SPACES_PATH'])

    def save_to_file(self, ical_file_data):
        """
            Save file locally. Pathname is defined in config.yml and is relative
            to the calling script's (main.py) directory.
        """
        print(" 5. Saving iCal to file..")
        file_path = os.path.join(self.main_root_path, settings.config['FILE_PATH'])
        with open(file_path, 'wb') as f:
            f.write(ical_file_data)
        print("    Saved to ", file_path)


    def generate(self):
        """
            Main function which orchestrates iCal file generation and saving
        """
        start_date, end_date = dates.get_start_end_dates()
        print(f"*** GENERATING ICAL FOR {self.timeoffs_group} TIMEOFFS."
              f" From {start_date} to {end_date}: ***")

        whos_out_data = self.get_whos_out_data(start_date, end_date)
        self.get_team_employees()

        timeoffs_data_for_ical = self.filter_timeoff_requests(whos_out_data)

        print(f" 4. Forming ical..")
        ical_file_data = ical.create_ical_file(timeoffs_data_for_ical,
                                               settings.config['ICAL_NAME'])

        #  SAVE_TO environment variable may be defined in docker-compose.yml.
        #    'file' makes no sense for serverless function,
        #      so 'dospaces' is the default value
        save_to = os.getenv('SAVE_TO', 'dospaces')

        if save_to == 'file':
            self.save_to_file(ical_file_data)
        else:
            self.upload_to_spaces(ical_file_data)

        print("*** ALL DONE. iCal generated and saved. ***")
        return

