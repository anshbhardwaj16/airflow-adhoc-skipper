from setuptools import setup, find_packages

setup(
    name="airflow-adhoc-skipper",
    version="0.1.0",
    description="Utility operator to skip unpause-triggered adhoc Airflow DAG runs",
    author="Your Name",
    packages=find_packages(),
    install_requires=["apache-airflow>=2.6"],
)
