import prefect
from prefect import task, Flow
from prefect.tasks.jupyter import ExecuteNotebook
from prefect.schedules import Schedule
from prefect.triggers import all_successful
from prefect.schedules.clocks import DatesClock, CronClock

from datetime import timedelta
import pendulum

from tasks.data_extraction import obtain_data

logger = prefect.context.get("logger")

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def dp_task():
    ExecuteNotebook(path='tasks/data_wrangling.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def pp_task():
    ExecuteNotebook(path='tasks/pre_processing.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def model_task():
    ExecuteNotebook(path='tasks/model.ipynb', kernel_name='python3').run()


@task
def data_extract():
    logger.info("Obteniendo datos...")
    obtain_data()
    logger.info("Datos obtenidos!")


scheduler = Schedule(
    clocks=[DatesClock([pendulum.now().add(seconds=10)]), CronClock("0 0 * * 0")],
    )

with Flow("spike-pipeline", schedule=scheduler) as flow:
    data_extract()
    dp_task(upstream_tasks=[data_extract])
    pp_task(upstream_tasks=[dp_task])
    model_task(upstream_tasks=[pp_task])

flow.run()