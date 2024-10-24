from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/live")
async def liveness_probe() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_probe(request: Request) -> dict:
    # Implement any additional checks to determine if the application is ready to accept traffic.
    return {"status": "ok"}
