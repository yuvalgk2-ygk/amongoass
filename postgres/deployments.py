import datetime
import uuid

from mongo.database import Database
from postgres import cursor, connection

def add_deployment(db: Database):
    insert_query = """
    INSERT INTO deployments (db_name, status, username, creation_time)
    VALUES (%s, %s, %s, %s);
    """

    data = (db.db_name, 'created', db.username, datetime.datetime.now())

    cursor.execute(insert_query, data)
    connection.commit()

def get_deployment_id(db: Database) -> uuid.UUID:
    select_query = """
    SELECT id FROM deployments
    WHERE db_name = %s and username = %s
    """

    data = (db.db_name, db.username)

    cursor.execute(select_query, data)
    connection.commit()

    return cursor.fetchone()

def get_deployment_postgres(deployment_id: uuid.UUID):
    select_query = f"""
    SELECT id, db_name, status, TO_CHAR(creation_time, 'YYYY-MM-DD HH24:MI:SS') FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()

def get_deployment_username(deployment_id: uuid.UUID):
    select_query = f"""
    SELECT username FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()[0]

def get_deployment_db_name(deployment_id: uuid.UUID):
    select_query = f"""
    SELECT db_name FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()[0]

def update_deployment_db_name(deployment_id: uuid.UUID, new_db_name: str):
    update_query = f"""
    UPDATE deployments
    SET db_name = '{new_db_name}'
    WHERE id = '{deployment_id}'
    """

    cursor.execute(update_query)
    connection.commit()