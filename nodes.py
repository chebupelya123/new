from dotenv import load_dotenv
from pydantic import BaseModel,Field,ConfigDict
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from state import ProjectState
from models import TechnicalSpecification
from prompts import (analysis_prompt,questions_prompt, plan_prompt, specification_prompt)


load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_retries=2
)


class AnalysisResult(BaseModel):

    model_config = ConfigDict(extra="forbid")

    analysis: str = Field(
        description="Объяснение результатов анализа проекта"
    )

    is_sufficient: bool = Field(
        description="Достаточно ли информации для разработки"
    )

    has_product: bool = Field(
        description="Указано ли, что необходимо разработать"
    )

    has_purpose: bool = Field(
        description="Указано ли назначение проекта"
    )

    has_features: bool = Field(
        description="Указаны ли основные функции проекта"
    )


    #Здесь пошла цепочка
analysis_chain=(
    analysis_prompt
        |llm.with_structured_output(
        AnalysisResult,
        method="json_schema",
        strict = True
    )
)
questions_chain = questions_prompt | llm | StrOutputParser()
plan_chain = plan_prompt | llm | StrOutputParser()

def analyze_project(state: ProjectState):
    print("\n[AI] Анализирую техническое задание...")

    result = analysis_chain.invoke({
        "project_description": state["project_description"],
    })

    is_sufficient = all([
        result.has_product,
        result.has_purpose,
        result.has_features
    ])
    return {
        "analysis": result.analysis,
        "is_sufficient": is_sufficient,

        "has_product": result.has_product,
        "has_purpose": result.has_purpose,
        "has_features": result.has_features
    }

def create_questions(state: ProjectState):
    print("\n[AI] Формирую уточняющие вопросы...")

    prompt_value = questions_prompt.invoke({
        "project_description": state["project_description"],
        "analysis": state["analysis"],
        "has_product": state["has_product"],
        "has_purpose": state["has_purpose"],
        "has_features": state["has_features"]
    })

    response = llm.invoke(prompt_value)

    return {
        "questions": response.content
    }

def create_plan(state: ProjectState):
    print("\n[AI] Составляю план разработки...")

    prompt_value = plan_prompt.invoke({
        "project_description": state["project_description"]
    })

    response = llm.invoke(prompt_value)

    return {
        "develop_plan": response.content
    }

def collect_answers(state: ProjectState):
    if state.get("answers"):
        return {"answers": state["answers"]}

    print("\n" + "=" * 60)
    print("          УТОЧНЯЮЩИЕ ВОПРОСЫ")
    print("=" * 60)

    print(state["questions"])

    print("\nВведите ответы на вопросы.")
    print("Можно использовать несколько строк.")
    print("Для завершения нажмите Enter на пустой строке.\n")

    lines = []

    while True:
        line = input()

        if not line.strip():
            break

        lines.append(line)

    answers = "\n".join(lines).strip()

    if not answers:
        print("\nВы не ввели ответы.")

    return {"answers": answers}

def update_description(state: ProjectState):
    print("\n[AI] Обновляю описание проекта...")

    updated_description = (
        state["project_description"]
        + "\n\nОтветы пользователя на уточняющие вопросы:\n"
        + state["answers"]
    )

    return {
        "project_description": updated_description,
        "iteration": state.get("iteration", 0) + 1
    }

def generate_specification(state: ProjectState):
    print("\n[AI]Формирую техническое задание...")
    try:
        prompt_value = specification_prompt.invoke({
            "project_description": state["project_description"]
        })

        structured_llm = llm.with_structured_output(
            TechnicalSpecification,
            method="json_schema",
            strict = True
        )

        response = structured_llm.invoke(prompt_value)
        print("[DEBUG] Техническое задание сформировано.")

        return {
            "specification": response.model_dump()
        }
    except Exception:
        import traceback

        print("\n[ERROR] Ошибка при создании технического задания:")
        traceback.print_exc()
        raise