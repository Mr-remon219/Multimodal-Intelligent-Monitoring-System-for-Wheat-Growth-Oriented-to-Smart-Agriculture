from django.db import connection

TABLE_PREFIX = "user_sensor_data_"


def get_user_sensor_table_name(user_id):
    return f"{TABLE_PREFIX}{int(user_id)}"


def ensure_user_sensor_table(user_id):
    table_name = get_user_sensor_table_name(user_id)
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        soil_type VARCHAR(20) NOT NULL,
        seedling_stage VARCHAR(20) NOT NULL,
        moi REAL NOT NULL,
        temp REAL NOT NULL,
        humidity REAL NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
    with connection.cursor() as cursor:
        cursor.execute(create_sql)
    return table_name


def insert_user_sensor_record(user_id, payload):
    table_name = ensure_user_sensor_table(user_id)
    insert_sql = f"""
    INSERT INTO "{table_name}" (soil_type, seedling_stage, moi, temp, humidity)
    VALUES (%s, %s, %s, %s, %s)
    """

    with connection.cursor() as cursor:
        cursor.execute(
            insert_sql,
            [
                payload["soil_type"],
                payload["seedling_stage"],
                payload["MOI"],
                payload["temp"],
                payload["humidity"],
            ],
        )
        row_id = cursor.lastrowid
    return table_name, row_id
