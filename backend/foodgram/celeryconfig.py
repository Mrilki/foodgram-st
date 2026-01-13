from .utils import build_broker_url, build_engine_url


broker_url = build_broker_url()
result_backend = build_engine_url("db+postgresql+psycopg2")


# Сериализация
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'

# Часовой пояс
timezone = 'UTC'
enable_utc = True
