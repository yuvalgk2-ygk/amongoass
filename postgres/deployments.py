import datetime
import uuid

from mongo_fastapi.models.database import Database
from postgres import cursor, connection

def add_deployment(db: Database):
    insert_query = """
    INSERT INTO deployments (db_name, status, username, creation_time)
    VALUES (%s, %s, %s, %s);
    """

    data = (db.db_name, 'created', db.username, datetime.datetime.now())

    cursor.execute(insert_query, data)
    connection.commit()

def check_deployment_id_exists(deployment_id: uuid.UUID):
    select_query = f"""
    SELECT * FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    if cursor.fetchone() is None:
        raise TypeError(f'There is no deployment by the id - {deployment_id}')

def get_deployment_id(db: Database) -> uuid.UUID:
    select_query = """
    SELECT id FROM deployments
    WHERE db_name = %s and username = %s
    """

    data = (db.db_name, db.username)

    cursor.execute(select_query, data)
    connection.commit()

    return cursor.fetchone()

def get_deployment_except_username(deployment_id: uuid.UUID):
    check_deployment_id_exists(deployment_id)

    select_query = f"""
    SELECT id, db_name, status, TO_CHAR(creation_time, 'YYYY-MM-DD HH24:MI:SS') FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()

def get_deployment_username(deployment_id: uuid.UUID):
    check_deployment_id_exists(deployment_id)

    select_query = f"""
    SELECT username FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()[0]

def get_deployment_db_name(deployment_id: uuid.UUID):
    check_deployment_id_exists(deployment_id)

    select_query = f"""
    SELECT db_name FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()[0]

def get_deployment_status(deployment_id: uuid.UUID):
    check_deployment_id_exists(deployment_id)

    select_query = f"""
    SELECT status FROM deployments
    WHERE id = '{deployment_id}'
    """

    cursor.execute(select_query)
    connection.commit()

    return cursor.fetchone()[0]

def check_deployment_username_permission(deployment_id: uuid.UUID, username: str):
    deployment_username = get_deployment_username(deployment_id)
    if deployment_username != username:
        raise PermissionError(f"Username {username} unauthorized to access database - not admin")

def check_deployment_status(deployment_id: uuid.UUID):
    deployment_status = get_deployment_status(deployment_id)
    if deployment_status == 'deleted':
        raise ValueError(f"The deployment status is deleted - database does not exist")


def update_status_deployment_delete(deployment_id: uuid.UUID, username: str):
    check_deployment_id_exists(deployment_id)
    check_deployment_username_permission(deployment_id, username)
    check_deployment_status(deployment_id)

    update_query = f"""
    UPDATE deployments
    SET status = 'deleted'
    WHERE id = '{deployment_id}'
    """

    cursor.execute(update_query)
    connection.commit()


def check_deployment_new_db_name(deployment_id: uuid.UUID, new_db_name: str):
    check_deployment_id_exists(deployment_id)
    username = get_deployment_username(deployment_id)

    if not new_db_name.startswith(username):
        raise TypeError(f'Invalid database name {new_db_name} - name must start with username {username}')

def update_deployment_db_name(deployment_id: uuid.UUID, new_db_name: str):
    check_deployment_new_db_name(deployment_id, new_db_name)
    check_deployment_status(deployment_id)

    update_query = f"""
    UPDATE deployments
    SET db_name = '{new_db_name}'
    WHERE id = '{deployment_id}'
    """

    cursor.execute(update_query)
    connection.commit()

