import os

def build_broker_url() -> str:
    """Construct broker connection string.

    Returns:
        str: Connection string
    """
    broker_host = os.getenv("BROKER_HOST")
    broker_port = os.getenv("BROKER_PORT")
    broker_password = os.getenv("BROKER_PASSWORD")
    broker_user = os.getenv("BROKER_USER")

    return f"amqp://{broker_user}:{broker_password}@{broker_host}:{broker_port}/"

def build_engine_url(schema="postgresql+psycopg2") -> str:
    """Construct DB connection string.

    Returns:
        str: connection string
    """
    database_host = os.getenv("DB_HOST")
    database_port = os.getenv("DB_PORT")
    database_name = os.getenv("POSTGRES_DB")
    database_password = os.getenv("POSTGRES_PASSWORD")
    database_user = os.getenv("POSTGRES_USER")
    return f"{schema}://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
