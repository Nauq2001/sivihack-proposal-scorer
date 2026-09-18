import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.v1.endpoints.MarkitDown.router import router as api_v1_router

load_dotenv(Path(__file__).with_name('.env'))

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)  # NOSONAR

app = FastAPI()

origins = [
    'http://localhost',
    'http://localhost:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=[],
)

# This function routes to version 1 of the REST API /v1/..
app.include_router(
    api_v1_router,
    prefix='/v1',
)

if __name__ == '__main__':
    logging.info('App is up and running')
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000)
