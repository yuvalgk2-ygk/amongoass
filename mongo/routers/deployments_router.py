import uuid

from fastapi import APIRouter, HTTPException, Response, status


from mongo.connect_mongo import client
from mongo.database import Database
from postgres.deployments import add_deployment, get_deployment_id, get_deployment_postgres
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

    add_deployment(db)
    deployment_id = get_deployment_id(db)
    LOGGER.info(f"Database {db.db_name} added to deployments table - id {deployment_id}")
    return Response(content=f"Database {db.db_name} added to deployments table - id {deployment_id}", status_code=status.HTTP_200_OK)


@deployment_router.get('/')
async def get_deployment(deployment_id: uuid.UUID):
    data = get_deployment_postgres(deployment_id)

    LOGGER.info(f"Returned {data} from the deployments table")
    return Response(content=f"{data}", status_code=status.HTTP_200_OK)

