from django.db import connection

TABLE_PREFIX = "user_sensor_data_"


def get_user_sensor_table_name(user_id):
    return f"{TABLE_PREFIX}{int(user_id)}"


def ensure_user_sensor_table(user_id):
    table_name = get_user_sensor_table_name(user_id)
    quoted_table_name = connection.ops.quote_name(table_name)
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {quoted_table_name} (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        soil_type VARCHAR(20) NOT NULL,
        seedling_stage VARCHAR(20) NOT NULL,
        moi DOUBLE NOT NULL,
        temp DOUBLE NOT NULL,
        humidity DOUBLE NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
    with connection.cursor() as cursor:
        cursor.execute(create_sql)
    return table_name


def insert_user_sensor_record(user_id, payload):
    table_name = ensure_user_sensor_table(user_id)
    quoted_table_name = connection.ops.quote_name(table_name)
    insert_sql = f"""
    INSERT INTO {quoted_table_name} (soil_type, seedling_stage, moi, temp, humidity)
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


def fetch_latest_user_sensor_record(user_id):
    table_name = ensure_user_sensor_table(user_id)
    quoted_table_name = connection.ops.quote_name(table_name)
    query_sql = f"""
    SELECT id, soil_type, seedling_stage, moi, temp, humidity, created_at
    FROM {quoted_table_name}
    ORDER BY id DESC
    LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query_sql)
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": int(row[0]),
        "soil_type": row[1],
        "seedling_stage": row[2],
        "MOI": float(row[3]),
        "temp": float(row[4]),
        "humidity": float(row[5]),
        "created_at": row[6],
    }
