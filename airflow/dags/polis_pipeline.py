import datetime
from airflow.sdk import dag
from airflow.providers.standard.operators.bash import BashOperator


@dag(start_date=datetime.datetime(2026, 6, 7), schedule="@once")
def polis_dag():
    load_ingestion = BashOperator(
        task_id="start_ingestion",
        bash_command="python /opt/airflow/src/ingestion.py",
        execution_timeout=datetime.timedelta(minutes=30),
        retries=3,
    )

    clean_senate = BashOperator(
        task_id="clean_senate_25",
        bash_command="""docker exec polis-ph-spark-1 /opt/spark/bin/spark-submit \
        --master spark://spark:7077 \
        --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.0 \
        --conf spark.jars.ivy=/tmp/.ivy \
        --name 'Cleaning Senate 25' \
        /opt/spark/jobs/cleaners.py raw_senate_25 /opt/spark/output/senate_25
        """,
        execution_timeout=datetime.timedelta(minutes=30),
        retries=3,
    )

    clean_partylist = BashOperator(
        task_id="clean_partylist_25",
        bash_command="""docker exec polis-ph-spark-1 /opt/spark/bin/spark-submit \
        --master spark://spark:7077 \
        --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.0 \
        --conf spark.jars.ivy=/tmp/.ivy \
        --name 'Cleaning Partylist 25' \
        /opt/spark/jobs/cleaners.py raw_partylist_25 /opt/spark/output/partylist_25
        """,
        execution_timeout=datetime.timedelta(minutes=30),
        retries=3,
    )

    # dependencies
    load_ingestion >> clean_senate >> clean_partylist  # type: ignore[operator]


polis_dag()
