import time
from tasks import reminder_wheater_today
from log_analytic import AnalyticLog
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

def reminder_cuaca():
    sched = BackgroundScheduler()
    sched.start()
    al = AnalyticLog()
    # for data in al.get_reminder('cuaca'):
    sched.add_job(reminder_wheater_today, 'cron', hour='13', minute="33", args=["U90a846efb4bc03eec9e66cbf61fea960", "-6.946494", "107.613608"])
    # sched.add_job(print_somtehing, 'cron', hour='15', minute="39", args=None)
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()

if __name__ == "__main__":
    
    reminder_cuaca()