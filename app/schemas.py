from pydantic import BaseModel,Field

class ProjectStartRequest(BaseModel):

    project_description:str = Field(
        min_length=5,
        max_length=10000,
        description="Описание пользователя проекта"
    )
class ProjectAnswerRequest(BaseModel):
    answers:str = Field(
        min_length=1,
        max_length=10000,
        description="Ответы пользователя на уточняющие вопросы"
    )
