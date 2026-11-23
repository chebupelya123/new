from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from app.database import SessionLocal
from app.models import Project
from export import export_to_pdf, export_to_docx
from app.schemas import ProjectStartRequest,ProjectAnswerRequest
from app.services import (
    start_project,
    continue_project,
    get_project_specification,
    save_project,
    save_project_answer,
    save_specification,
    load_project
)
from graph import web_app
import traceback

app = FastAPI(
    title = "AI Technical Specification Generator",
    description="AI-сервис для анализа требований и создания ТЗ",
    version="1.0.0"
)
templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)
@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.get("/api/projects")
def get_projects():

    db = SessionLocal()

    try:
        projects = db.query(Project).order_by(
            Project.created_at.desc()
        ).all()

        return [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "thread_id": project.thread_id,
                "created_at": (
                    project.created_at.isoformat()
                    if project.created_at else None
                ),
                "updated_at": (
                    project.updated_at.isoformat()
                    if project.updated_at else None
                )
            }
            for project in projects
        ]

    except Exception as error:
        print(f"[ERROR] Ошибка получения проектов: {error}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении списка проектов"
        )

    finally:
        db.close()


@app.get("/api/projects/{project_id}")
def get_project(project_id: int):
    try:
        project = load_project(project_id)

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Проект не найден"
            )

        return project

    except HTTPException:
        raise

    except Exception as error:
        print(f"[ERROR] Ошибка загрузки проекта: {error}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Ошибка при загрузке проекта"
        )

@app.post("/api/projects/start")
def start_new_project(request: ProjectStartRequest):

    thread_id = str(uuid4())

    try:
        # Запускаем AI-анализ
        result = start_project(
            project_description=request.project_description,
            thread_id=thread_id,
        )

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        snapshot = web_app.get_state(config)

        # Определяем статус проекта
        if "collect_answers" in snapshot.next:
            status = "needs_answers"

        elif result.get("specification"):
            status = "completed"

        else:
            status = "failed"

        # Сохраняем проект в MariaDB
        project_id = save_project(
            project_description=request.project_description,
            thread_id=thread_id,
            status=status
        )

        print(f"[DB] Сохранён проект ID: {project_id}")

        # Если ТЗ создано сразу, сохраняем его в MariaDB
        if status == "completed":
            specification = result.get("specification")

            if specification:
                save_specification(
                    thread_id=thread_id,
                    content=specification
                )

                print(
                    f"[DB] Техническое задание сохранено для проекта {project_id}"
                )

        # Возвращаем результат клиенту
        if status == "needs_answers":
            return {
                "thread_id": thread_id,
                "status": "needs_answers",
                "analysis": result.get("analysis"),
                "questions": result.get("questions"),
            }

        if status == "completed":
            return {
                "thread_id": thread_id,
                "status": "completed",
                "analysis": result.get("analysis"),
                "specification": result.get("specification"),
            }

        return {
            "thread_id": thread_id,
            "status": "failed",
            "analysis": result.get("analysis"),
        }

    except Exception as e:
        print(f"[ERROR] Ошибка запуска проекта: {e}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Ошибка при обработке проекта"
        )

@app.post("/api/projects/{thread_id}/answers")
def submit_project_answer(
        thread_id: str,
        request: ProjectAnswerRequest,
):
    try:
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        # Получаем состояние ДО продолжения графа
        snapshot_before = web_app.get_state(config)

        old_questions = snapshot_before.values.get("questions", "")
        old_iteration = snapshot_before.values.get("iteration", 0)

        # Продолжаем работу LangGraph
        result = continue_project(
            answers=request.answers,
            thread_id=thread_id
        )

        # Сохраняем вопросы и ответы пользователя
        save_project_answer(
            thread_id=thread_id,
            iteration=old_iteration + 1,
            questions=old_questions,
            answers=request.answers
        )

        # Получаем обновлённое состояние
        snapshot = web_app.get_state(config)

        # Проверяем, нужны ли ещё ответы
        if "collect_answers" in snapshot.next:
            return {
                "thread_id": thread_id,
                "status": "needs_answers",
                "analysis": result.get("analysis"),
                "questions": result.get("questions")
            }

        # Проверяем, создано ли техническое задание
        specification = result.get("specification")

        if specification:
            save_specification(
                thread_id=thread_id,
                content=specification
            )

            return {
                "thread_id": thread_id,
                "status": "completed",
                "analysis": result.get("analysis"),
                "specification": specification
            }

        return {
            "thread_id": thread_id,
            "status": "incomplete",
            "analysis": result.get("analysis")
        }

    except Exception as error:
        print(f"[ERROR] Ошибка продолжения проекта: {error}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Ошибка при продолжении обработки проекта"
        )
@app.post("/api/projects/{thread_id}/export/pdf")
def export_project_pdf(thread_id: str):
    try:
        specification = get_project_specification(thread_id)

        file_path = export_to_pdf(specification)

        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type='application/pdf',
        )
    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(f"[ERROR] Ошибка экспорта PDF: {error}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Ошибка при создании PDF"
        )
@app.post("/api/projects/{thread_id}/export/docx")
def export_project_docx(thread_id: str):
    try:
        specification = get_project_specification(thread_id)
        file_path = export_to_docx(specification)
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(f"[ERROR] Ошибка экспорта DOCX: {error}")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Ошибка при создании DOCX"
        )
