import pytest
import pendulum
from airflow_adhoc_skipper.operators.skip_adhoc import SkipIfAdhocRunOperator
from airflow.exceptions import AirflowSkipException

class DummyDagRun:
    def __init__(self, run_id):
        self.run_id = run_id

def make_context(run_id, logical_date):
    return {
        "dag_run": DummyDagRun(run_id),
        "logical_date": logical_date,
    }

def test_manual_run_proceeds():
    op = SkipIfAdhocRunOperator(task_id="test")
    context = make_context("manual__2025-10-31T12:00:00+00:00", pendulum.datetime(2025, 10, 31, 12, 0, 0, tz="UTC"))
    # Should not raise
    op.execute(context)

def test_scheduled_run_within_threshold_proceeds():
    op = SkipIfAdhocRunOperator(task_id="test", threshold_seconds=60)
    logical_date = pendulum.now("UTC").subtract(seconds=30)
    context = make_context("scheduled__2025-10-31T12:00:00+00:00", logical_date)
    # Should not raise
    op.execute(context)

def test_scheduled_run_exceeds_threshold_skips():
    op = SkipIfAdhocRunOperator(task_id="test", threshold_seconds=60)
    logical_date = pendulum.now("UTC").subtract(seconds=120)
    context = make_context("scheduled__2025-10-31T12:00:00+00:00", logical_date)
    with pytest.raises(AirflowSkipException):
        op.execute(context)
