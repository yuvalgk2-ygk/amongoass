import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status, Header, Body

from mongo_fastapi.models.db_name import DatabaseName
from mongo_fastapi.mongo import add_database, delete_database
from mongo_fastapi.models.database import Database
from postgres.deployments import (add_deployment, get_deployment_id, get_deployment_except_username,
                                  update_deployment_db_name, get_deployment_db_name, update_status_deployment_delete,
                                  check_deployment_id_exists, check_deployment_status,
                                  check_deployment_username_permission)
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

deployment_router = APIRouter(prefix="/deployments", tags=["deployments"])


@deployment_router.post('/')
async def create_database(db: Database):
    try:
        add_database(db)
        LOGGER.info(f"Database {db.db_name} was successfully added")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    add_deployment(db)
    deployment_id = get_deployment_id(db)
    LOGGER.info(f"Database {db.db_name} added to deployments table - id {deployment_id}")

    return Response(content=f"Database {db.db_name} added to mongoDB cluster & deployments table - id {deployment_id}", status_code=status.HTTP_200_OK)


@deployment_router.get('/')
async def get_deployment(deployment_id: uuid.UUID):
    try:
        data = get_deployment_except_username(deployment_id)
        LOGGER.info(f"Returned {data} from the deployments table")
        return Response(content=f"{data}", status_code=status.HTTP_200_OK)

    except TypeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@deployment_router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(deployment_id: uuid.UUID, username: Annotated[str, Header()]):
    try:
        update_status_deployment_delete(deployment_id, username)
        LOGGER.info(f"Updated deployment status to deleted - id: {deployment_id}")

    except TypeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    db_name = get_deployment_db_name(deployment_id)
    delete_database(db_name)
    LOGGER.info(f"Deleted database {db_name} from mongoDB cluster")


@deployment_router.get('/connection_string/')
async def get_deployment_connection_string(deployment_id: uuid.UUID, username: Annotated[str, Header()]):
    #not finished!
    try:
        check_deployment_id_exists(deployment_id)
        check_deployment_status(deployment_id)
        check_deployment_username_permission(deployment_id, username)
        LOGGER.info(f"Deployment {deployment_id} exists and user {username} is the admin")

    except TypeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    #get connection string of database - not finished
    db_name = get_deployment_db_name(deployment_id)
    connection_string = ''

    LOGGER.info(f"Returned {connection_string} of deployment {deployment_id}")
    return Response(content=f"{connection_string}", status_code=status.HTTP_200_OK)


@deployment_router.put('/')
async def update_deployment_name(deployment_id: Annotated[uuid.UUID, Header()], db_name: DatabaseName):
    #not finished!
    new_db_name = db_name.db_name
    old_db_name = get_deployment_db_name(deployment_id)

    try:
        update_deployment_db_name(deployment_id, new_db_name)
        LOGGER.info(f"Updated deployment db_name to {new_db_name} in the deployments table - {deployment_id}")

    except TypeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


    #rename db in mongo_fastapi cluster - not finished
    LOGGER.info(f"Updated db_name to {new_db_name} in the mongoDB cluster")
    return Response(content=f"{new_db_name} is now the name of the data base", status_code=status.HTTP_200_OK)


