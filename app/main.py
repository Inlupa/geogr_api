from fastapi import FastAPI, HTTPExeption, Depends
from pydantic import Basemodel
from typing import List, Annotated

app = FastAPI()

class ChoiseBase(baseModel):
    chice_text:str
    is_correct: bool
    
class QuestionBase(BaseModel):
    question_text:str
    choices:List[ChoiseBase]
