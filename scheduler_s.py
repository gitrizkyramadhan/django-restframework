import time
from tasks import reminder_wheater_today
from log_analytic import AnalyticLog
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

def reminder_cuaca():
    sched = BlockingScheduler()
    sched.start()
    al = AnalyticLog()
    # for data in al.get_reminder('cuaca'):
    sched.add_job(reminder_wheater_today, 'cron', hour='6', args=[])
    # try:
    #     while True:
    #         time.sleep(2)
    # except (KeyboardInterrupt, SystemExit):
    #     # Not strictly necessary if daemonic mode is enabled but should be done if possible
    #     sched.shutdown()

if __name__ == "__main__":
    
    reminder_cuaca()