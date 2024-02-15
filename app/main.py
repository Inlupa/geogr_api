from fastapi import FastAPI, HTTPExeption, Depends
from pydantic import Basemodel
from typing import List, Annotated

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
