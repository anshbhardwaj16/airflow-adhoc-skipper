# 🪄 airflow-adhoc-skipper

**Skip unintentional or stale Airflow DAG runs automatically.**  
This lightweight operator helps you **avoid accidental adhoc DAG executions** — for example, when a paused DAG is unpaused and Airflow triggers an old run or multiple backfilled runs unintentionally.

---

## 🚀 Why This Exists

When a DAG with `catchup=False` is unpaused after being idle for a while, Airflow may still schedule a "late" run.  
These runs are technically valid but often **not desired**, especially in production pipelines where you only care about *the next scheduled execution*, not *old missed ones*.

This operator lets you **gracefully detect and skip such adhoc runs** — without failing the DAG — ensuring your downstream tasks stay clean and consistent.

---

## ⚙️ How It Works

At runtime, the operator:

1. Checks if the current DAG run is **manual** (`run_id` starts with `"manual__"`).  
   - ✅ Manual runs proceed normally.
2. Otherwise, it compares the `logical_date` (scheduled execution time) to the **current UTC time**.
3. If the delay exceeds a configured threshold (default: 60 seconds), the operator:
   - Logs the delay.
   - Marks the task as **skipped**.
   - Propagates skip status to downstream tasks.

**This behavior ensures:**
- Scheduled runs execute as expected.
- Unpause-triggered or stale runs get skipped cleanly.
- Downstream operators are never executed accidentally.

---

## 🧩 Installation

```bash
pip install git+https://github.com/<your-username>/airflow-adhoc-skipper.git
```

---

## 📦 Requirements

- Apache Airflow >= 2.6
- Python >= 3.8
- pendulum (already part of Airflow)

---

## 🧠 Example DAG Usage

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow_adhoc_skipper.operators.skip_adhoc import SkipIfAdhocRunOperator
from datetime import datetime

with DAG(
    dag_id="example_skip_adhoc",
    start_date=datetime(2025, 10, 31),
    schedule_interval="*/10 * * * *",
    catchup=False,
    tags=["utility", "scheduler-safety"],
) as dag:

    # This task ensures the DAG run is valid
    check = SkipIfAdhocRunOperator(
        task_id="check_adhoc_run",
        threshold_seconds=60,  # Skip if run is >1 minute delayed
    )

    # This task executes only for valid runs
    main = BashOperator(
        task_id="main_job",
        bash_command="echo 'Main job executing...'"
    )

    check >> main
```

---

## 🗺️ Graph View

```
check_adhoc_run (skip on stale runs)
        ↓
     main_job
```

---

## 🧭 Behavior Summary

| Scenario                                 | Run ID                                 | Result      |
|------------------------------------------|----------------------------------------|-------------|
| Manual trigger from UI                   | manual__2025-10-31T12:00:00+00:00      | ✅ Pass     |
| Scheduled on time                        | scheduled__2025-10-31T12:00:00+00:00   | ✅ Pass     |
| Scheduled but heavily delayed (unpause)  | scheduled__2025-10-31T10:00:00+00:00   | ⚠️ Skipped  |

---

## ⚡ Parameters

| Parameter         | Type | Default | Description                                                                 |
|-------------------|------|---------|-----------------------------------------------------------------------------|
| threshold_seconds | int  | 60      | Maximum allowed difference (in seconds) between now and scheduled execution time before skipping. |

---

## 🧰 Development

Clone and install locally in editable mode:

```bash
git clone https://github.com/<your-username>/airflow-adhoc-skipper.git
cd airflow-adhoc-skipper
pip install -e .
```

To run tests (optional):

```bash
pytest tests/
```

---

## 🧱 Project Structure

```
airflow-adhoc-skipper/
├── airflow_adhoc_skipper/
│   ├── __init__.py
│   └── operators/
│       └── skip_adhoc.py
├── setup.py
├── README.md
└── LICENSE
```

---

## 🛡️ License

This project is licensed under the Apache 2.0 License, the same as Apache Airflow.

---

## 🤝 Contributing

Contributions, ideas, and discussions are welcome!
You can:
- Open issues for feedback or feature requests.
- Submit pull requests for bug fixes or improvements.
- Share your Airflow DAG examples where this operator helped.

---

## ❤️ Acknowledgements

Built by Airflow practitioners who got tired of unpause-triggered ghost runs breaking clean DAG histories 😄
Inspired by the need for production-safe, idempotent scheduling.

---

## 🧭 Quick Summary

✅ Prevents unwanted backfill/adhoc runs  
✅ Works seamlessly with Airflow DAGs  
✅ Skips cleanly — no DAG failures  
✅ Fully compatible with manual and scheduled runs  
✅ Minimal code, no extra dependencies

---
