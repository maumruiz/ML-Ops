import prefect
from prefect import task, Flow
from prefect.schedules import Schedule
from prefect.triggers import all_successful
from prefect.schedules.clocks import DatesClock, CronClock

from tasks.jupyter.jupyter import ExecuteNotebook

from datetime import timedelta
import pendulum

from tasks.data_extraction import obtain_data

logger = prefect.context.get("logger")

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def data_wrangling(task_input):
    ExecuteNotebook(path='tasks/data_wrangling.ipynb', output_path='logs/out_data_wrangling.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def data_visualization(task_input):
    ExecuteNotebook(path='tasks/data_visualization.ipynb', output_path='logs/out_data_visualization.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def pre_processing(task_input):
    ExecuteNotebook(path='tasks/pre_processing.ipynb', output_path='logs/out_pre_processing.ipynb', kernel_name='python3').run()

@task(max_retries=3, retry_delay=timedelta(seconds=30), trigger=all_successful)
def model_training(task_input):
    ExecuteNotebook(path='tasks/model_training.ipynb', output_path='logs/out_model_training.ipynb', kernel_name='python3').run()


@task
def data_extract():
    logger.info("Obteniendo datos...")
    obtain_data()
    logger.info("Datos obtenidos!")


scheduler = Schedule(
    clocks=[DatesClock([pendulum.now().add(seconds=10)]), CronClock("0 0 * * 0")],
    )

with Flow("spike-pipeline", schedule=scheduler) as flow:
    out1 = data_extract()
    out2 = data_wrangling(task_input=out1)
    out3_1 = pre_processing(task_input=out2)
    out3_2 = data_visualization(task_input=out2)
    out4 = model_training(task_input=out3_1)

flow.run()