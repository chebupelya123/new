from graph import web_app
from app.database import SessionLocal
from app.models import Project, ProjectAnswer, Specification

def start_project(project_description:str, thread_id:str):

    initial_state = {
        "project_description": project_description,
        "iteration":0,
        "answers":""
    }

    config = {
        "configurable":{
            "thread_id":thread_id,
        }
    }

    result = web_app.invoke(
        initial_state,config=config,
    )
    return result

def continue_project(answers:str,thread_id:str):

    config = {
        "configurable":{
            "thread_id":thread_id,
        }
    }

    web_app.update_state(
        config,
        {"answers":answers},
        as_node = "collect_answers"
    )
    result = web_app.invoke(
        None,
        config=config,
    )
    return result

def get_project_specification(thread_id:str):

    config = {
        "configurable":{
            "thread_id":thread_id,
        }
    }
    snapshot = web_app.get_state(config)

    specification = snapshot.values.get("specification")
    if not specification:
        raise Exception("Specification not create")
    return specification

def save_project(
        project_description:str,
        thread_id:str,
        status:str
):
    db = SessionLocal()

    try:
        title = " ".join(project_description.strip().split())[:60]
        if not title:
            title="New project"
        project = Project(
            title=title,
            description=project_description,
            status=status,
            thread_id=thread_id
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        print(f"[DB]Project {project.id} saved")

        return project.id
    except Exception as error:
        db.rollback()
        print(f"[DB ERROR] Ошибка сохранения проекта: {error}")
        raise
    finally:
        db.close()

def save_project_answer(
        thread_id: str,
        iteration: int,
        questions: str,
        answers: str
):
    db = SessionLocal()

    try:
        project = db.query(Project).filter(
            Project.thread_id == thread_id
        ).first()

        if not project:
            raise Exception(f"Проект с thread_id {thread_id} не найден")

        answer_record = ProjectAnswer(
            project_id=project.id,
            iteration=iteration,
            questions=questions,
            answers=answers
        )

        db.add(answer_record)
        db.commit()
        db.refresh(answer_record)

        print(f"[DB] Ответ сохранён. ID: {answer_record.id}")

        return answer_record.id

    except Exception as error:
        db.rollback()
        print(f"[DB ERROR] Ошибка сохранения ответа: {error}")
        raise

    finally:
        db.close()

def save_specification(thread_id: str, content: dict):
    import json

    db = SessionLocal()

    try:
        project = db.query(Project).filter(
            Project.thread_id == thread_id
        ).first()

        if not project:
            raise Exception(f"Проект с thread_id {thread_id} не найден")

        specification = db.query(Specification).filter(
            Specification.project_id == project.id
        ).first()

        content_json = json.dumps(
            content,
            ensure_ascii=False,
            indent=4
        )

        if specification:
            specification.content = content_json
        else:
            specification = Specification(
                project_id=project.id,
                content=content_json
            )
            db.add(specification)

        db.commit()

        print(f"[DB] Техническое задание сохранено для проекта {project.id}")

    except Exception as error:
        db.rollback()
        print(f"[DB ERROR] Ошибка сохранения ТЗ: {error}")
        raise

    finally:
        db.close()


def load_project(project_id: int):
    import json

    db = SessionLocal()

    try:
        project = db.query(Project).filter(
            Project.id == project_id
        ).first()

        # Получаем сохранённое состояние LangGraph
        config = {
            "configurable": {
                "thread_id": project.thread_id
            }
        }

        graph_snapshot = web_app.get_state(config)

        graph_values = graph_snapshot.values or {}

        graph_questions = graph_values.get("questions")
        graph_next = list(graph_snapshot.next)

        if not project:
            return None

        # Получаем историю вопросов и ответов
        answers = db.query(ProjectAnswer).filter(
            ProjectAnswer.project_id == project.id
        ).order_by(
            ProjectAnswer.iteration.asc()
        ).all()

        # Получаем техническое задание
        specification = db.query(Specification).filter(
            Specification.project_id == project.id
        ).first()

        specification_content = None

        if specification and specification.content:
            specification_content = json.loads(
                specification.content
            )

        return {
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
            ),

            "answers": [
                {
                    "id": answer.id,
                    "iteration": answer.iteration,
                    "questions": answer.questions,
                    "answers": answer.answers,
                    "created_at": (
                        answer.created_at.isoformat()
                        if answer.created_at else None
                    )
                }
                for answer in answers
            ],

            "specification": specification_content,
            "graph_questions": graph_questions,
            "graph_next": graph_next,
        }

    except Exception as error:
        print(f"[DB ERROR] Ошибка загрузки проекта: {error}")
        raise

    finally:
        db.close()
