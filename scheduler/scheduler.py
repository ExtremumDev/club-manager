import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger

from .event_jobs import send_random_user


def setup_default_jobs(scheduler: AsyncIOScheduler):
    scheduler.add_job(
        func=send_random_user,
        trigger=CronTrigger(day_of_week=0, hour=10, minute=0, second=0),
        jobstore="memory"
    )


jobstores = {
    'default': RedisJobStore(
        host='localhost',
        port=6379,
        db=0,
        jobs_key='apscheduler.jobs',
        run_times_key='apscheduler.run_times'
    ),
    'memory': MemoryJobStore()
}

executors = {
    'default': ThreadPoolExecutor(20)
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors
)


