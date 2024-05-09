import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .config import logger, executor
from .routers.router import api_router
from .database import engine, Base

app = FastAPI()
app.mount("/files", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
Base.metadata.create_all(bind=engine)
@app.on_event("startup")
def on_startup():
    # Initialize resources
    pass

@app.on_event("shutdown")
def on_shutdown():
    # Close the executor
    executor.shutdown(wait=True)
    logger.info("Executor has been shut down")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



