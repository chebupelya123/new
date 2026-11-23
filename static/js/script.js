
function renderSpecification(specification) {

    resultSection.innerHTML = "";

    // Заголовок документа
    const title = document.createElement("h2");
    title.textContent = specification.overview?.title || "Техническое задание";
    resultSection.appendChild(title);

    // Общая информация
    const overview = document.createElement("section");
    overview.className = "spec-block";
    overview.innerHTML = "<h3>Общая информация</h3>";

    const description = document.createElement("p");
    description.textContent = specification.overview?.description || "";
    overview.appendChild(description);

    const purpose = document.createElement("p");
    purpose.textContent = "Цель проекта: " + (specification.overview?.purpose || "Не указана");
    overview.appendChild(purpose);

    const audience = document.createElement("p");
    audience.textContent = "Целевая аудитория: " + (specification.overview?.target_audience || "Не указана");
    overview.appendChild(audience);

    resultSection.appendChild(overview);


    // Функциональные требования
    const functional = document.createElement("section");
    functional.className = "spec-block";
    functional.innerHTML = "<h3>Функциональные требования</h3>";

    (specification.functional_requirements || []).forEach(item => {
        const block = document.createElement("div");
        block.className = "requirement-item";

        const name = document.createElement("h4");
        name.textContent = item.name;

        const text = document.createElement("p");
        text.textContent = item.description;

        const priority = document.createElement("span");
        priority.textContent = "Приоритет: " + item.priority;

        block.append(name, text, priority);
        functional.appendChild(block);
    });

    resultSection.appendChild(functional);

    // Технические требования
    const technical = document.createElement("section");
    technical.className = "spec-block";
    technical.innerHTML = "<h3>Технические требования</h3>";

    (specification.technical_requirements || []).forEach(item => {
        ["frontend", "backend", "database"].forEach(key => {
            const p = document.createElement("p");
            p.textContent = key.toUpperCase() + ": " + (item[key] || "Не определено");
            technical.appendChild(p);
        });

        const integrations = document.createElement("p");
        integrations.textContent = "Интеграции: " +
            ((item.integration || []).join(", ") || "Не определены");
        technical.appendChild(integrations);
    });

    resultSection.appendChild(technical);

    // Критерии приемки
    const acceptance = document.createElement("section");
    acceptance.className = "spec-block";
    acceptance.innerHTML = "<h3>Критерии приёмки</h3>";

    (specification.acceptance_criterion || []).forEach(item => {
        const block = document.createElement("div");
        block.className = "requirement-item";

        const requirement = document.createElement("h4");
        requirement.textContent = item.requirement;

        const expected = document.createElement("p");
        expected.textContent = item.expected_result;

        block.append(requirement, expected);
        acceptance.appendChild(block);
    });

    resultSection.appendChild(acceptance);

    // План разработки
    const plan = document.createElement("section");
    plan.className = "spec-block";
    plan.innerHTML = "<h3>План разработки</h3>";

    const list = document.createElement("ol");

    (specification.develop_plan || []).forEach(step => {
        const li = document.createElement("li");
        li.textContent = step;
        list.appendChild(li);
    });

    plan.appendChild(list);
    resultSection.appendChild(plan);

    // Кнопки экспорта
const exportSection = document.createElement("div");
exportSection.className = "export-buttons";

const pdfButton = document.createElement("button");
pdfButton.textContent = "Скачать PDF";
pdfButton.addEventListener("click", () => {
    downloadDocument("pdf");
});

const docxButton = document.createElement("button");
docxButton.textContent = "Скачать DOCX";
docxButton.addEventListener("click", () => {
    downloadDocument("docx");
});

exportSection.append(pdfButton, docxButton);
resultSection.appendChild(exportSection);

}

// Получаем элементы HTML
const startButton = document.getElementById("start-button");
const projectDescription = document.getElementById("project-description");
const resultSection = document.getElementById("result-section");
const historyButton = document.getElementById("history-button");
const projectHistory = document.getElementById("project-history");

console.log("SCRIPT.JS УСПЕШНО ЗАГРУЖЕН");
console.log("historyButton:", historyButton);
console.log("projectHistory:", projectHistory);

let currentThreadId=null;

async function loadProjects() {
    projectHistory.innerHTML = "<p>Загрузка проектов...</p>";

    try {
        const response = await fetch("/api/projects");
        const projects = await response.json();

        if (!response.ok) {
            throw new Error(projects.detail || "Не удалось загрузить проекты");
        }

        renderProjectHistory(projects);

    } catch (error) {
        console.error("Ошибка загрузки проектов:", error);
        projectHistory.innerHTML = "<p>Ошибка загрузки проектов</p>";
    }
}


function renderProjectHistory(projects) {
    projectHistory.innerHTML = "";

    if (!projects.length) {
        projectHistory.innerHTML = "<p>Пока нет проектов</p>";
        return;
    }

    projects.forEach(project => {
        const item = document.createElement("div");
        item.className = "history-project";
        item.addEventListener("click", () => {
        console.log("Клик по проекту:", project.id);
        openProject(project.id);
        });

        const title = document.createElement("div");
        title.className = "history-project-title";
        title.textContent = project.title;

        const status = document.createElement("div");
        status.className = "history-project-status";
        status.textContent = project.status;

        const date = document.createElement("div");
        date.className = "history-project-date";
        date.textContent = project.created_at
            ? new Date(project.created_at).toLocaleString("ru-RU")
            : "";

        item.append(title, status, date);
        projectHistory.appendChild(item);
    });
}

//New label

async function openProject(projectId) {
    console.log("Вызвана openProject, ID:", projectId);
    resultSection.classList.remove("hidden");
    resultSection.innerHTML = "<p>Загружаем проект...</p>";

    try {

        const response = await fetch(`/api/projects/${projectId}`);
        const project = await response.json();

        if (!response.ok) {
            throw new Error(
                project.detail || "Не удалось загрузить проект"
            );
        }

        // Восстанавливаем идентификатор проекта
        currentThreadId = project.thread_id;

        // Восстанавливаем исходное описание
        projectDescription.value = project.description || "";


// Если техническое задание уже существует
if (project.specification) {

    renderSpecification(project.specification);

// Если LangGraph ожидает ответы пользователя
} else if (
    project.graph_questions &&
    project.graph_next &&
    project.graph_next.includes("collect_answers")
) {

    console.log("Восстановленные вопросы:", project.graph_questions);
    console.log("Следующий узел графа:", project.graph_next);

    renderQuestions(project.graph_questions);

// Если есть история предыдущих ответов
} else if (project.answers && project.answers.length > 0) {

    resultSection.innerHTML = `
        <h2>${project.title}</h2>
        <p>Проект загружен.</p>
        <h3>История уточнений</h3>
    `;

    project.answers.forEach(answer => {

        const block = document.createElement("section");
        block.className = "spec-block";

        const questions = document.createElement("p");
        questions.textContent = "Вопросы: " + (answer.questions || "");

        const answers = document.createElement("p");
        answers.textContent = "Ответы: " + answer.answers;

        block.append(questions, answers);
        resultSection.appendChild(block);

    });

} else {

    resultSection.innerHTML = `
        <h2>${project.title}</h2>
        <p>${project.description}</p>
        <p>Сохранённый проект пока не содержит технического задания.</p>
    `;

}


        console.log("Проект загружен:", project);

    } catch (error) {

        console.error("Ошибка загрузки проекта:", error);

        resultSection.innerHTML = `
            <h2>Ошибка загрузки проекта</h2>
            <p>${error.message}</p>
        `;

    }
}


function renderQuestions(questions) {

    resultSection.innerHTML = "";

    console.log("Полученные вопросы:", questions);


// Преобразуем вопросы в массив
let questionList = [];

if (Array.isArray(questions)) {

    questionList = questions;

} else if (typeof questions === "string") {

    // Находим позиции начала каждого пронумерованного вопроса
    const markers = [...questions.matchAll(/(?:^|\s)\d+[.)]\s*/g)];

    if (markers.length > 0) {

        markers.forEach((marker, index) => {

            const start = marker.index + marker[0].length;

            const end = index + 1 < markers.length
                ? markers[index + 1].index
                : questions.length;

            const question = questions
                .slice(start, end)
                .trim();

            if (question.length > 0) {
                questionList.push(question);
            }

        });

    } else {

        questionList = [questions.trim()];

    }

} else {

    questionList = [questions];

}




    // Заголовок
    const title = document.createElement("h2");
    title.textContent = "Уточняющие вопросы";
    resultSection.appendChild(title);

    const description = document.createElement("p");
    description.textContent =
        "AI необходимо получить дополнительную информацию о вашем проекте.";
    resultSection.appendChild(description);

    // Контейнер карточек
    const questionsContainer = document.createElement("div");
    questionsContainer.className = "questions-container";

    // Создаём отдельную карточку для каждого вопроса
    questionList.forEach((question, index) => {

        const card = document.createElement("div");
        card.className = "question-card";

        const number = document.createElement("div");
        number.className = "question-number";
        number.textContent = String(index + 1).padStart(2, "0");

        const text = document.createElement("p");

        if (typeof question === "string") {
            text.textContent = question;
        } else if (question && typeof question === "object") {
            text.textContent =
                question.question ||
                question.text ||
                JSON.stringify(question);
        } else {
            text.textContent = String(question);
        }

        card.append(number, text);
        questionsContainer.appendChild(card);

    });

    resultSection.appendChild(questionsContainer);


    // Контейнер для дополнительных ответов
    const answersForm = document.createElement("div");
    answersForm.className = "answers-form";

    // Поле для ответов
    const textarea = document.createElement("textarea");
    textarea.id = "answers-input";
    textarea.className = "answers-input";
    textarea.placeholder = "Введите ответы на уточняющие вопросы...";
    textarea.rows = 7;

    // Кнопка отправки
    const button = document.createElement("button");
    button.id = "submit-answers-button";
    button.className = "submit-answers-button";
    button.textContent = "Отправить ответы";

    // Добавляем элементы в контейнер
    answersForm.append(textarea, button);

    // Добавляем контейнер в результат
    resultSection.appendChild(answersForm);

    // Обработчик отправки
    button.addEventListener("click", submitAnswers);


    console.log("Количество карточек:", questionList.length);
}




async function submitAnswers() {

    const answersInput = document.getElementById("answers-input");
    const button = document.getElementById("submit-answers-button");

    const answers = answersInput.value.trim();

    if (!answers) {
        alert("Пожалуйста, заполните ответы.");
        return;
    }

    if (!currentThreadId) {
        alert("Не найден ID проекта. Начните анализ заново.");
        return;
    }

    button.disabled = true;
    button.textContent = "Отправляем ответы...";

    try {

        const response = await fetch(
            `/api/projects/${encodeURIComponent(currentThreadId)}/answers`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    answers: answers
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Ошибка отправки ответов");
        }

        console.log("Ответ после уточнения:", data);

        if (data.status === "needs_answers") {

        console.log("СТАТУС:", data.status);
        console.log("ПОЛНЫЙ ОТВЕТ:", data);

        renderQuestions(data.questions);

        } else if (data.status === "completed") {

            renderSpecification(data.specification);

        } else {

            resultSection.innerHTML = `
                <h2>Анализ не завершён</h2>
                <p>AI пока не смог сформировать техническое задание.</p>
            `;

        }

    } catch (error) {

        console.error("Ошибка:", error);

        resultSection.innerHTML = `
            <h2>Ошибка отправки ответов</h2>
            <p>${error.message}</p>
        `;

    }
}

// Обработка нажатия кнопки
startButton.addEventListener("click", async () => {

    // Получаем описание проекта
    const description = projectDescription.value.trim();

    // Проверяем, что пользователь ввёл текст
    if (description.length < 5) {
        alert("Пожалуйста, опишите проект подробнее.");
        return;
    }

    // Блокируем кнопку на время обработки
    startButton.disabled = true;
    startButton.textContent = "Анализируем...";

    // Показываем область результатов
    resultSection.classList.remove("hidden");
    resultSection.innerHTML = "<p>AI анализирует ваш проект. Пожалуйста, подождите...</p>";

    try {

        // Отправляем запрос в FastAPI
        const response = await fetch("/api/projects/start", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                project_description: description
            })
        });

        // Получаем ответ сервера
        const data = await response.json();

        // Проверяем HTTP-статус
        if (!response.ok) {
            throw new Error(data.detail || "Ошибка сервера");
        }

        console.log("Ответ API:", data);
        console.log("ВОПРОСЫ ОТ AI:", data.questions);
        console.log("ТИП ВОПРОСОВ:", typeof data.questions);
        console.log("ЭТО МАССИВ:", Array.isArray(data.questions));

        currentThreadId = data.thread_id;

        // Проверяем статус обработки
        if (data.status === "needs_answers") {

            renderQuestions(data.questions);

        } else if (data.status === "completed") {

            renderSpecification(data.specification);

        } else {

            resultSection.innerHTML = `
                <h2>Не удалось обработать проект</h2>
                <p>Попробуйте изменить описание и повторить запрос.</p>
            `;

        }

    } catch (error) {

        console.error("Ошибка:", error);

        resultSection.innerHTML = `
            <h2>Ошибка</h2>
            <p>${error.message}</p>
        `;

    } finally {

        // Возвращаем кнопку в исходное состояние
        startButton.disabled = false;
        startButton.innerHTML = 'Начать анализ <span>→</span>';

    }

});

async function downloadDocument(format) {

    if (!currentThreadId) {
        alert("Не найден ID проекта. Начните анализ заново.");
        return;
    }

    const endpoint =
        `/api/projects/${encodeURIComponent(currentThreadId)}/export/${format}`;

    try {

        const response = await fetch(endpoint, {
            method: "POST"
        });

        if (!response.ok) {

            let errorMessage = "Не удалось создать документ";

            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // Если сервер вернул не JSON, используем стандартное сообщение
            }

            throw new Error(errorMessage);
        }

        // Получаем файл
        const blob = await response.blob();

        // Создаём временную ссылку
        const url = window.URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;

        // Имя файла
        const extension = format === "pdf" ? "pdf" : "docx";
        link.download = `technical_specification.${extension}`;

        document.body.appendChild(link);
        link.click();

        // Удаляем временные ресурсы
        link.remove();
        window.URL.revokeObjectURL(url);

    } catch (error) {

        console.error("Ошибка экспорта:", error);
        alert(error.message);

    }
}

// Загружаем историю при наведении на пункт меню
historyButton.addEventListener("mouseenter", loadProjects);