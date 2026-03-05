import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status, Header, Body

from mongo.models.db_name import DatabaseName
from mongo.mongo import client
from mongo.models.database import Database
from postgres.deployments import add_deployment, get_deployment_id, get_deployment_postgres, get_deployment_username, \
    update_deployment_db_name, get_deployment_db_name, delete_db, get_deployment_status
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

deployment_router = APIRouter(prefix="/deployments", tags=["deployments"])


@deployment_router.post('')
async def create_database(db: Database):
    if db.db_name in client.list_database_names():
        raise HTTPException(status_code=409, detail="Database already exists")

    new_db = client[db.db_name]
    new_collection = new_db[db.collection_name]
    if len(db.data) == 1:
        new_collection.insert_one(db.data[0])
    elif len(db.data) > 1:
        new_collection.insert_many(db.data)
    LOGGER.info(f"Database {db.db_name} added to mongoDB cluster")

    add_deployment(db)
    deployment_id = get_deployment_id(db)
    LOGGER.info(f"Database {db.db_name} added to deployments table - id {deployment_id}")
    return Response(content=f"Database {db.db_name} added to mongoDB cluster & deployments table - id {deployment_id}", status_code=status.HTTP_200_OK)


@deployment_router.get('/')
async def get_deployment(deployment_id: uuid.UUID):
    data = get_deployment_postgres(deployment_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Deployment not found")

    LOGGER.info(f"Returned {data} from the deployments table")
    return Response(content=f"{data}", status_code=status.HTTP_200_OK)


@deployment_router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(deployment_id: uuid.UUID, username: Annotated[str, Header()]):

    deployment_username = get_deployment_username(deployment_id)
    if deployment_username != username:
        raise HTTPException(status_code=403, detail=f'the username {username} is not the admin of the database {deployment_id} and therefore not authorized')

    deployment_status = get_deployment_status(deployment_id)
    if deployment_status == 'deleted':
        raise HTTPException(status_code=404, detail="Database not found - deployment is deleted")

    delete_db(deployment_id)
    LOGGER.info(f"Updated deployment status to deleted - id: {deployment_id} ")

    db_name = get_deployment_db_name(deployment_id)
    client.drop_database(db_name)
    LOGGER.info(f"Deleted database {db_name} from mongoDB cluster")


@deployment_router.put('/')
async def update_deployment_name(deployment_id: Annotated[uuid.UUID, Header()], db_name: DatabaseName):

    deployment_status = get_deployment_status(deployment_id)
    if deployment_status == 'deleted':
        raise HTTPException(status_code=404, detail="Database not found - deployment is deleted")

    new_db_name = db_name.db_name
    username = get_deployment_username(deployment_id)

    if not new_db_name.startswith(username):
        raise HTTPException(status_code=422, detail=f'Invalid database name - name must start with username: {username}')


    update_deployment_db_name(deployment_id, new_db_name)
    LOGGER.info(f"Updated db_name to {new_db_name} in the deployments table")

    #rename db in mongo cluster - not finished
    old_db_name = get_deployment_db_name(deployment_id)
    LOGGER.info(f"Updated db_name to {new_db_name} in the mongoDB cluster")

    return Response(content=f"{new_db_name} is now the name of the data base", status_code=status.HTTP_200_OK)


