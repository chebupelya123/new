from pydantic import BaseModel, Field

class ProjectOverview(BaseModel):
    title: str = Field(description="Название проекта")
    description: str = Field(description="Короткое описание проекта")
    purpose: str = Field(description="Цель разработки")
    target_audience: str = Field(description="Целевая аудитория")

class FunctionalRequirement(BaseModel):
    name: str = Field(description="Название функции")
    description: str = Field(description="Описание функции")
    priority: str = Field(
        description="Приоритет: высокий, средний, низкий"
    )

class TechnicalRequirement(BaseModel):
    frontend: str = Field(description="Требования к frontend")
    backend: str = Field(description="Требования к backend")
    database: str = Field(description="Требования к database")
    integration: list[str] = Field(description="Внешние интеграции")

class AcceptanceCriterion(BaseModel):
    requirement: str = Field(description="Проверяемое требование")
    expected_result: str = Field(description="Ожидаемый результат")

class TechnicalSpecification(BaseModel):
    overview: ProjectOverview
    functional_requirements: list[FunctionalRequirement]
    technical_requirements: list[TechnicalRequirement]
    acceptance_criterion: list[AcceptanceCriterion]
    develop_plan: list[str]