from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger as log


class JobScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.job_names: set[str] = set()

    def add_job(
        self,
        job: Callable,
        interval_seconds: int | None = None,
        args: list[Any] | None = None,
        run_immediately: bool = True,
    ) -> None:
        async def wrapped() -> Any:
            try:
                return await job(*args or [])
            except Exception as e:
                log.error(
                    "exception in background task {}, exception: {}", job.__name__, e
                )

        self.job_names.add(job.__name__)

        if interval_seconds is not None:
            self.scheduler.add_job(
                wrapped,
                trigger=IntervalTrigger(seconds=interval_seconds),
                id=job.__name__,
                name=job.__name__,
            )
        if run_immediately:
            self.scheduler.add_job(
                wrapped,
                misfire_grace_time=None,
                id=f"{job.__name__}_immediate",
                name=job.__name__,
            )

    def add_one_time_job(
        self, job: Callable, delay_seconds: int = 0, args: list[Any] | None = None
    ) -> None:
        async def wrapped() -> Any:
            try:
                return await job(*args or [])
            except Exception as e:
                log.error(
                    "exception in background task {}, exception: {}", job.__name__, e
                )

        run_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.job_names.add(job.__name__)
        self.scheduler.add_job(wrapped, trigger=DateTrigger(run_date=run_time))

    def add_cron_job(
        self,
        job: Callable,
        hour: int,
        minute: int,
        timezone: str = "UTC",
        args: list[Any] | None = None,
    ) -> None:
        async def wrapped() -> Any:
            try:
                return await job(*args or [])
            except Exception as e:
                log.error(
                    "exception in background task {}, exception: {}", job.__name__, e
                )

        self.job_names.add(job.__name__)
        # Schedule the job based on the cron trigger with timezone
        self.scheduler.add_job(
            wrapped,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
            id=job.__name__,
        )

    def start(self) -> None:
        log.debug("starting job scheduler")
        self.scheduler.start()
        log.debug("job scheduler started")

    def stop(self) -> None:
        log.debug("stopping job scheduler with jobs: {}", ", ".join(self.job_names))
        self.scheduler.shutdown(wait=True)
        log.debug("job scheduler stopped")

    def list_jobs(self) -> None:
        log.debug("Currently scheduled jobs: {}", ", ".join(self.job_names))

    def remove_job(self, job: Callable) -> None:
        self.scheduler.remove_job(job.__name__)
