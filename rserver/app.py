from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rserver.api import router as api_router
from rserver.transaction import router as transaction_router
from rserver.validators import router as  validators_router
from rserver.status import router as status_router
from rserver.testnet import router as testnet_router
app = FastAPI()

app.include_router(api_router)
app.include_router(transaction_router)
app.include_router(validators_router)
app.include_router(status_router)
app.include_router(testnet_router)

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