import uvicorn
from fastapi import FastAPI

from mongo.routers.deployments_router import deployment_router

app = FastAPI()

app.include_router(deployment_router)

def initialize_app():
    uvicorn.run(app, host='localhost', port=8080)
    return app


if __name__ == "__main__":
    initialize_app()
