from typing import TypedDict

class ProjectState(TypedDict, total=False):

    project_description: str
    analysis:str


    is_sufficient: bool
    has_product: bool
    has_purpose: bool
    has_features: bool

    questions: str
    answers: str
    develop_plan: str
    specification:dict
    iteration: int

