import datetime

def get_start_end_dates():
    """
        Define start and end dates for the Who's Out data request
    """
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=today.weekday())
    end_date = start_date + datetime.timedelta(weeks=4)
    return start_date, end_date

def get_requests_range():
    """
        Get date range limiting the margins of time off requests.
        This range is wider than Who's Out:
          currently -3mo;+5mo from today
    """
    today = datetime.date.today()

    # Calculate the date 90 days ago
    requests_from = today - datetime.timedelta(days=30*3)

    # Calculate the date 150 days from now
    requests_to = today + datetime.timedelta(days=30*5)
    return requests_from, requests_to