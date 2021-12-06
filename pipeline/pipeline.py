import prefect
from prefect import task, Flow
from prefect.tasks.jupyter import ExecuteNotebook
from datetime import timedelta
from prefect.schedules import Schedule
from prefect.schedules.clocks import DatesClock, CronClock
import pendulum

from tasks.data_extraction import obtain_data

logger = prefect.context.get("logger")

@task(max_retries=3, retry_delay=timedelta(seconds=30))
def dp_task():
    ExecuteNotebook(path='tasks/data_wrangling.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30))
def pp_task():
    ExecuteNotebook(path='tasks/pre_processing.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30))
def model_task():
    ExecuteNotebook(path='tasks/model.ipynb', kernel_name='python3').run()

@task
def data_extract():
    logger.info("Obteniendo datos...")
    obtain_data()
    logger.info("Datos obtenidos!")

# scheduler = CronSchedule(
#     cron='0 0 * * 0'
# )

scheduler = Schedule(
    clocks=[DatesClock([pendulum.now().add(minutes=1)]), CronClock("0 0 * * 0")],
    )

with Flow("spike-pipeline", schedule=scheduler) as flow:
    data_extract()
    dp_task()
    pp_task()
    model_task()

flow.run()