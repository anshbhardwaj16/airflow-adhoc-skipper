from airflow.models import BaseOperator
from airflow.exceptions import AirflowSkipException
import pendulum

class SkipIfAdhocRunOperator(BaseOperator):
    """
    SkipIfAdhocRunOperator
    This custom Airflow operator is designed to skip DAG runs that are triggered manually or due to an unpause event,
    unless the run occurs within a specified threshold of seconds from the scheduled execution date.
    Features:
    - Skips runs with a delay greater than `threshold_seconds` (default: 60 seconds).
    - Allows manual runs (run_id starts with "manual__") to proceed.
    - Logs informative messages for each decision path.
    - Raises AirflowSkipException to skip the task when an adhoc run is detected.
    Args:
        threshold_seconds (int, optional): Maximum allowed delay (in seconds) between the scheduled execution date and the actual run time.
            Runs with a delay greater than this value are considered adhoc and will be skipped. Defaults to 60.
        **kwargs: Additional keyword arguments passed to BaseOperator.
    Raises:
        AirflowSkipException: If the run is detected as adhoc (delay exceeds threshold_seconds).
    Usage:
        Use this operator in DAGs where you want to prevent execution of tasks for adhoc or unpause-triggered runs,
        ensuring only legitimate scheduled runs proceed.
    """
    def __init__(self, threshold_seconds=60, **kwargs):
        super().__init__(**kwargs)
        self.threshold_seconds = threshold_seconds

    def execute(self, context):
        dag_run = context["dag_run"]
        run_id = dag_run.run_id
        execution_date = context["logical_date"]
        now_utc = pendulum.now("UTC")

        if run_id.startswith("manual__"):
            self.log.info("Manual run detected — proceeding.")
            return

        delay = (now_utc - execution_date).total_seconds()
        if delay > self.threshold_seconds:
            self.log.warning("Skipping adhoc/unpause-triggered run (delay %.2fs).", delay)
            raise AirflowSkipException("Detected adhoc run. Skipping.")
        self.log.info("Legit scheduled run — continuing.")
