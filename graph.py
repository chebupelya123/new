from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from state import ProjectState
import sqlite3
from nodes import (
    analyze_project,
    create_questions,
    create_plan,
    collect_answers,
    update_description,
    generate_specification
)


MAX_ITERATIONS = 3


def route_project(state: ProjectState):

    if state["is_sufficient"]:
        return "create_plan"

    if state.get("iteration", 0) >= MAX_ITERATIONS:
        return END

    return "create_questions"


workflow = StateGraph(ProjectState)


# Регистрируем узлы
workflow.add_node("analyze_project", analyze_project)
workflow.add_node("create_questions", create_questions)
workflow.add_node("collect_answers", collect_answers)
workflow.add_node("update_description", update_description)
workflow.add_node("create_plan", create_plan)
workflow.add_node("generate_specification", generate_specification)


# Начало процесса
workflow.add_edge(START, "analyze_project")


# Проверяем результат анализа
workflow.add_conditional_edges(
    "analyze_project",
    route_project,
    {
        "create_plan": "create_plan",
        "create_questions": "create_questions",
        END: END
    }
)


# Цикл уточнения
workflow.add_edge("create_questions", "collect_answers")
workflow.add_edge("collect_answers", "update_description")
workflow.add_edge("update_description", "analyze_project")


# Завершение
workflow.add_edge("create_plan", "generate_specification")
workflow.add_edge("generate_specification", END)


app = workflow.compile()

conn = sqlite3.connect("langgraph_checkpoint.sqlite",check_same_thread=False)

web_memory = SqliteSaver(conn)

web_app = workflow.compile(
    checkpointer=web_memory,
    interrupt_before=["collect_answers"]
)