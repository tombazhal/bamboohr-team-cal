from typing import List, TypedDict
import datetime
from icalendar import Calendar, Event

class TimeoffData(TypedDict):
    date: datetime.date
    description: str
    time_off_id: str

def create_ical_file(timeoffs_data: List[TimeoffData], ical_name):
    cal = Calendar()
    cal.add('prodid', '-//BhrTeamCal//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', ical_name)

    for event_data in timeoffs_data:
        event = Event()
        event.add('summary', event_data['description'])
        event.add('dtstart', event_data['date'])
        event.add('dtend', event_data['date'] + datetime.timedelta(days=1))
        event.add('dtstamp', datetime.datetime.now())
        event.add('uid', f"{event_data['date']}-{event_data['time_off_id']}@bhrteamcal")
        cal.add_component(event)

    return cal.to_ical()