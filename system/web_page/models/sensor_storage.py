from django.db import connection

TABLE_PREFIX = "user_sensor_data_"
USER_TABLE_NAME = "web_page_user"


def get_user_sensor_table_name(user_id):
    return f"{TABLE_PREFIX}{int(user_id)}"


def _has_column(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
        LIMIT 1
        """,
        [table_name, column_name],
    )
    return cursor.fetchone() is not None


def _has_user_id_index(cursor, table_name):
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = 'user_id'
        LIMIT 1
        """,
        [table_name],
    )
    return cursor.fetchone() is not None


def _has_user_id_foreign_key(cursor, table_name):
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_schema = kcu.constraint_schema
         AND tc.table_name = kcu.table_name
         AND tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_schema = DATABASE()
          AND tc.table_name = %s
          AND tc.constraint_type = 'FOREIGN KEY'
          AND kcu.column_name = 'user_id'
        LIMIT 1
        """,
        [table_name],
    )
    return cursor.fetchone() is not None


def _ensure_user_sensor_table_schema(cursor, table_name, user_id):
    normalized_user_id = int(user_id)
    quoted_table_name = connection.ops.quote_name(table_name)
    quoted_user_table_name = connection.ops.quote_name(USER_TABLE_NAME)

    if not _has_column(cursor, table_name, "user_id"):
        cursor.execute(f"ALTER TABLE {quoted_table_name} ADD COLUMN user_id BIGINT NULL AFTER id")

    cursor.execute(
        f"UPDATE {quoted_table_name} SET user_id = %s WHERE user_id IS NULL OR user_id <> %s",
        [normalized_user_id, normalized_user_id],
    )
    cursor.execute(f"ALTER TABLE {quoted_table_name} MODIFY COLUMN user_id BIGINT NOT NULL")

    if not _has_user_id_index(cursor, table_name):
        cursor.execute(f"ALTER TABLE {quoted_table_name} ADD INDEX (user_id)")

    if not _has_user_id_foreign_key(cursor, table_name):
        cursor.execute(
            f"""
            ALTER TABLE {quoted_table_name}
            ADD FOREIGN KEY (user_id) REFERENCES {quoted_user_table_name}(id)
            ON DELETE CASCADE
            """
        )


def ensure_user_sensor_table(user_id):
    table_name = get_user_sensor_table_name(user_id)
    quoted_table_name = connection.ops.quote_name(table_name)
    quoted_user_table_name = connection.ops.quote_name(USER_TABLE_NAME)
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {quoted_table_name} (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        soil_type VARCHAR(20) NOT NULL,
        seedling_stage VARCHAR(20) NOT NULL,
        moi DOUBLE NOT NULL,
        temp DOUBLE NOT NULL,
        humidity DOUBLE NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX (user_id),
        FOREIGN KEY (user_id) REFERENCES {quoted_user_table_name}(id) ON DELETE CASCADE
    )
    """
    with connection.cursor() as cursor:
        cursor.execute(create_sql)
        _ensure_user_sensor_table_schema(cursor, table_name, user_id)
    return table_name


def insert_user_sensor_record(user_id, payload):
    normalized_user_id = int(user_id)
    table_name = ensure_user_sensor_table(normalized_user_id)
    quoted_table_name = connection.ops.quote_name(table_name)
    insert_sql = f"""
    INSERT INTO {quoted_table_name} (user_id, soil_type, seedling_stage, moi, temp, humidity)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    with connection.cursor() as cursor:
        cursor.execute(
            insert_sql,
            [
                normalized_user_id,
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
