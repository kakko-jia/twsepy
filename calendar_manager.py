import exchange_calendars as ecals

class CalendarManager:
    def __init__(self, calendar_name="XTAI"):
        self.calendar = ecals.get_calendar(calendar_name)

    def get_trading_dates(self, start_date, end_date):
        schedule = self.calendar.schedule.loc[start_date:end_date]
        trading_dates = schedule.index
        return trading_dates
