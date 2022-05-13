from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rserver.validators import router as  validators_router
from rserver.status import router as status_router
app = FastAPI()

app.include_router(validators_router)
app.include_router(status_router)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)