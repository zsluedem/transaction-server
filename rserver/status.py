from fastapi import APIRouter

from pydantic import BaseModel
router = APIRouter()

class StatusResponse(BaseModel):
    status: str

@router.get('/status')
async def handle_status():
    return StatusResponse(status='ok')
