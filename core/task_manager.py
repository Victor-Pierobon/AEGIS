from apscheduler.schedulers.background import BackgroundScheduler
from plyer import notification
import dateparser

class OperationalCoordinator:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def set_alert(self, time_string):
        alarm_time = dateparser.parse(time_string)
        self.scheduler.add_job(
            self._trigger_alert,
            'date',
            run_date=alarm_time
        )
        return f"Alert confirmed for {alarm_time.strftime('%H:%M:%S ZULU')}"

    def _trigger_alert(self):
        notification.notify(
            title='A.E.G.I.S. Alert',
            message='Scheduled protocol activated',
            timeout=10
        )