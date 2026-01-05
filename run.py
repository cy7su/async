import hashlib
import json
import logging
import os

from flask import Flask, render_template
from flask_caching import Cache
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CrystalLexer, PythonLexer, RustLexer, get_lexer_by_name
from pygments.util import ClassNotFound

app = Flask(__name__)


log_dir = "/root/logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "async.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
app.logger.addHandler(
    logging.FileHandler(os.path.join(log_dir, "async.log"), encoding="utf-8")
)
app.logger.setLevel(logging.INFO)

app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600
cache = Cache(app)


def highlight_code(code, language):
    try:
        if language == "crystal":
            lexer = CrystalLexer()
        elif language == "rust":
            lexer = RustLexer()
        elif language == "python":
            lexer = PythonLexer()
        else:
            lexer = get_lexer_by_name(language)

        formatter = HtmlFormatter(
            style="monokai", cssclass="highlight", linenos=False, wrapcode=True
        )

        highlighted = highlight(code, lexer, formatter)
        return highlighted
    except ClassNotFound:
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    except Exception as e:
        print(f"Ошибка подсветки: {e}")
        return f'<pre><code class="language-{language}">{code}</code></pre>'


LANGUAGES = [
    {
        "name": "Crystal",
        "slug": "crystal",
        "description": "Современный компилируемый язык программирования с синтаксисом Ruby.",
        "features": [
            {
                "title": "Статическая типизация",
                "description": "Crystal использует статическую типизацию для обеспечения безопасности типов на этапе компиляции. Это позволяет выявлять ошибки до выполнения программы и обеспечивает лучшую производительность.",
            },
            {
                "title": "Производительность C",
                "description": "Благодаря компиляции в нативный код, Crystal достигает производительности, сравнимой с C. Это делает его идеальным для высоконагруженных приложений и системного программирования.",
            },
            {
                "title": "Синтаксис Ruby",
                "description": "Crystal наследует элегантный и выразительный синтаксис Ruby, что делает код читаемым и приятным для написания. Разработчики Ruby могут легко перейти на Crystal.",
            },
            {
                "title": "Автоматическое управление памятью",
                "description": "Crystal использует сборщик мусора для автоматического управления памятью, что избавляет разработчиков от ручного управления памятью и предотвращает утечки памяти.",
            },
            {
                "title": "Макросы и метапрограммирование",
                "description": "Мощная система макросов позволяет генерировать код во время компиляции, что обеспечивает гибкость и производительность. Это особенно полезно для создания DSL и оптимизации кода.",
            },
        ],
        "history": {
            "creator": "Ари Борер (Ary Borenszweig)",
            "creator_wiki": "https://en.wikipedia.org/wiki/Ary_Borenszweig",
            "year": "2011",
            "inspiration": "Ruby, C, Go",
            "development": "Crystal был создан как попытка объединить элегантность Ruby с производительностью C. Первая версия 0.1.0 вышла в 2014 году. Язык развивался медленно, но стабильно, достигнув версии 1.0 в 2021 году. Разработка велась небольшой командой энтузиастов, которые стремились создать язык, который был бы так же приятен для написания, как Ruby, но компилировался в быстрый нативный код. Ключевыми особенностями стали статическая типизация, вывод типов и мощная система макросов. Язык прошел через множество итераций, включая изменения в синтаксисе и системе типов.",
            "impact": "Crystal повлиял на развитие других языков, показав, что можно совместить высокоуровневый синтаксис с низкоуровневой производительностью. Вдохновил создание похожих языков в других экосистемах.",
            "future": "Язык продолжает развиваться, фокусируясь на веб-разработке и системном программировании. Планируется улучшение производительности компилятора и расширение экосистемы.",
        },
        "projects": [
            {
                "name": "Lucky Framework",
                "description": "Полнофункциональный веб-фреймворк для Crystal, вдохновленный Ruby on Rails. Lucky предоставляет мощные генераторы кода, встроенную ORM с миграциями, автоматическую валидацию данных, систему маршрутизации и middleware. Фреймворк фокусируется на type safety и производительности, предлагая compile-time проверки и быструю разработку. Включает в себя встроенную поддержку WebSockets, фоновых задач, кеширования и тестирования. Lucky идеально подходит для создания масштабируемых веб-приложений с акцентом на безопасность типов и developer experience.",
                "github": "https://github.com/luckyframework/lucky",
                "code_example": """
class Users::Index < BrowserAction
  get "/users" do
    users = UserQuery.new
    render IndexPage, users: users
  end
end""",
            },
            {
                "name": "Kemal",
                "description": "Быстрый, эффективный и простой веб-фреймворк для Crystal, вдохновленный Sinatra и Express.js. Kemal предоставляет минималистичный подход к веб-разработке с фокусом на производительность и простоту использования. Фреймворк поддерживает middleware, WebSockets, статические файлы, CORS, сессии и cookies. Благодаря компиляции в нативный код, Kemal показывает отличную производительность и низкое потребление памяти. Идеально подходит для создания API, микросервисов, real-time приложений и простых веб-сайтов с высокой нагрузкой.",
                "github": "https://github.com/kemalcr/kemal",
                "code_example": """
require "kemal"

get "/" do
  "Hello World!"
end

Kemal.run""",
            },
            {
                "name": "Crystal HTTP",
                "description": "Мощный HTTP клиент для Crystal с поддержкой HTTP/1.1, HTTP/2, WebSockets и множества других возможностей. Библиотека предоставляет синхронный и асинхронный API, поддержку SSL/TLS, автоматическое сжатие, cookies, редиректы и таймауты. Crystal HTTP используется для создания API клиентов, веб-скрапинга, интеграции с внешними сервисами и построения микросервисов. Библиотека оптимизирована для производительности и предоставляет удобный API для работы с HTTP протоколом в Crystal приложениях.",
                "github": "https://github.com/crystal-lang/crystal",
                "code_example": """
require "http/client"

client = HTTP::Client.new("https://api.example.com")
response = client.get("/users")
puts response.body""",
            },
            {
                "name": "Amber Framework",
                "description": "Полнофункциональный веб-фреймворк для Crystal, предоставляющий генераторы, ORM, маршрутизацию, middleware и многое другое. Amber вдохновлен Ruby on Rails и предоставляет аналогичную структуру проекта с контроллерами, моделями, представлениями и маршрутами. Фреймворк включает в себя встроенную ORM с миграциями, систему аутентификации, поддержку WebSockets, фоновых задач и кеширования. Amber идеально подходит для разработки масштабируемых веб-приложений с акцентом на производительность и developer experience.",
                "github": "https://github.com/amberframework/amber",
                "code_example": """
class UsersController < ApplicationController
  def index
    users = User.all
    render("index.slang")
  end
end""",
            },
        ],
        "icon": "crystal",
    },
    {
        "name": "Rust",
        "slug": "rust",
        "description": "Системный язык программирования с фокусом на безопасность и производительность.",
        "features": [
            {
                "title": "Безопасность памяти без сборщика мусора",
                "description": "Rust гарантирует безопасность памяти через систему владения и заимствования, исключая целый класс ошибок (null pointer, use-after-free, data races) без использования сборщика мусора.",
            },
            {
                "title": "Высокая производительность",
                "description": "Rust компилируется в эффективный машинный код с нулевой стоимостью абстракций. Производительность сравнима с C/C++, но с дополнительными гарантиями безопасности.",
            },
            {
                "title": "Параллельное программирование",
                "description": "Rust делает параллельное программирование безопасным через систему владения. Невозможно создать data races, что упрощает написание многопоточных приложений.",
            },
            {
                "title": "Система владения",
                "description": "Уникальная система владения Rust обеспечивает автоматическое управление памятью без сборщика мусора. Каждое значение имеет единственного владельца, что предотвращает утечки памяти.",
            },
            {
                "title": "Макросы и метапрограммирование",
                "description": "Процедурные макросы позволяют генерировать код во время компиляции, создавая мощные абстракции и DSL. Это обеспечивает гибкость без потери производительности.",
            },
        ],
        "history": {
            "creator": "Грейдон Хоар (Graydon Hoare)",
            "creator_wiki": "https://en.wikipedia.org/wiki/Graydon_Hoare",
            "year": "2006",
            "inspiration": "C++, ML, Haskell, Erlang",
            "development": "Rust начал разрабатываться в Mozilla как альтернатива C++. Первая версия 0.1 вышла в 2012 году. Язык прошел через множество итераций, включая кардинальные изменения в синтаксисе. Стабильная версия 1.0 была выпущена в 2015 году. Разработка велась под руководством Mozilla Research, с участием большого сообщества разработчиков. Ключевыми инновациями стали система владения (ownership), заимствование (borrowing) и lifetimes. Язык прошел через несколько major breaking changes, включая изменения в синтаксисе макросов и системы модулей.",
            "impact": "Rust революционизировал системное программирование, доказав, что можно достичь безопасности памяти без сборщика мусора. Используется в критически важных системах: браузеры, операционные системы, блокчейн.",
            "future": "Rust продолжает расти в популярности, особенно в области веб-разработки, благодаря фреймворкам как Actix и Rocket. Планируется улучшение ergonomics и расширение экосистемы.",
        },
        "projects": [
            {
                "name": "Tokio",
                "description": "Асинхронная среда выполнения для Rust, предоставляющая высокопроизводительные примитивы для создания сетевых приложений. Tokio включает в себя асинхронный runtime, TCP/UDP сокеты, таймеры, файловый I/O, синхронизацию и многое другое. Библиотека построена на основе epoll, kqueue и IOCP для максимальной производительности на разных платформах. Tokio используется в production системах для создания высоконагруженных серверов, микросервисов, real-time приложений и сетевых протоколов. Предоставляет удобный API для работы с асинхронным кодом и является основой для многих других Rust библиотек.",
                "github": "https://github.com/tokio-rs/tokio",
                "code_example": """// Асинхронный HTTP сервер
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    loop {
        let (socket, _) = listener.accept().await?;
        tokio::spawn(async move {
            // Обработка соединения
        });
    }
}""",
            },
            {
                "name": "Serde",
                "description": "Мощный фреймворк для сериализации и десериализации данных в Rust с поддержкой множества форматов. Serde поддерживает JSON, YAML, TOML, MessagePack, BSON, XML и многие другие форматы с высокой производительностью и безопасностью типов. Библиотека использует derive макросы для автоматической генерации кода сериализации, обеспечивая compile-time проверки и оптимизации. Serde широко используется в экосистеме Rust для работы с конфигурационными файлами, API, базами данных и межязыкового взаимодействия. Предоставляет гибкий API для кастомизации процесса сериализации.",
                "github": "https://github.com/serde-rs/serde",
                "code_example": """// Сериализация JSON
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    age: u32,
}

let user = User { name: "Alice".to_string(), age: 30 };
let json = serde_json::to_string(&user)?;""",
            },
            {
                "name": "Actix Web",
                "description": "Один из самых быстрых и мощных веб-фреймворков для Rust, основанный на actor model и асинхронном программировании. Actix Web предоставляет высокопроизводительный HTTP сервер с поддержкой WebSockets, middleware, маршрутизации, валидации данных и аутентификации. Фреймворк оптимизирован для создания высоконагруженных API, микросервисов и real-time приложений. Включает в себя встроенную поддержку CORS, сжатия, логирования, метрик и тестирования. Actix Web используется в production для создания масштабируемых веб-сервисов с акцентом на производительность и безопасность.",
                "github": "https://github.com/actix/actix-web",
                "code_example": """// Веб-API с Actix
use actix_web::{web, App, HttpServer, Result};

async fn index() -> Result<&'static str> {
    Ok("Hello World!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().route("/", web::get().to(index)))
        .bind("127.0.0.1:8080")?
        .run()
        .await
}""",
            },
            {
                "name": "Rust Analyzer",
                "description": "Языковой сервер для Rust, предоставляющий мощные возможности для разработки в IDE. Rust Analyzer включает в себя автодополнение кода, рефакторинг, анализ ошибок, навигацию по коду, поиск определений и ссылок, форматирование кода и многое другое. Инструмент использует статический анализ для предоставления точных подсказок и проверок в реальном времени. Rust Analyzer критически важен для эффективной разработки на Rust, значительно улучшая developer experience и продуктивность. Поддерживается всеми популярными редакторами и IDE через Language Server Protocol.",
                "github": "https://github.com/rust-lang/rust-analyzer",
                "code_example": """// Rust Analyzer LSP
// Автоматически предоставляет:
// - Автодополнение
// - Рефакторинг
// - Анализ ошибок
// - Навигация по коду""",
            },
        ],
        "icon": "rust",
    },
    {
        "name": "Python",
        "slug": "python",
        "description": "Высокоуровневый язык программирования общего назначения с акцентом на читаемость кода.",
        "features": [
            {
                "title": "Простой и читаемый синтаксис",
                "description": 'Python использует отступы для группировки кода, что делает его очень читаемым. Философия "красивое лучше уродливого" делает код понятным даже для новичков.',
            },
            {
                "title": "Большая стандартная библиотека",
                "description": "Python поставляется с обширной стандартной библиотекой, включающей модули для работы с файлами, сетью, регулярными выражениями, XML, JSON и многим другим.",
            },
            {
                "title": "Кроссплатформенность",
                "description": "Python работает на всех основных операционных системах (Windows, macOS, Linux) без изменений в коде. Это обеспечивает переносимость приложений между платформами.",
            },
            {
                "title": "Динамическая типизация",
                "description": "Python использует динамическую типизацию, что делает его гибким и быстрым для прототипирования. Типы определяются во время выполнения, что упрощает разработку.",
            },
            {
                "title": "Активное сообщество",
                "description": "Python имеет огромное и активное сообщество разработчиков, которое создает библиотеки для любых задач: веб-разработка, анализ данных, машинное обучение, автоматизация.",
            },
        ],
        "history": {
            "creator": "Гвидо ван Россум (Guido van Rossum)",
            "creator_wiki": "https://en.wikipedia.org/wiki/Guido_van_Rossum",
            "year": "1991",
            "inspiration": "ABC, Modula-3, C, Java",
            "development": 'Python был создан как хобби-проект Гвидо ван Россума во время рождественских каникул 1989 года. Первая версия 0.9.0 вышла в 1991 году. Python 2.0 (2000) и Python 3.0 (2008) стали ключевыми вехами в развитии языка. Разработка велась под руководством "Benevolent Dictator For Life" (BDFL) Гвидо ван Россума до 2018 года. Ключевыми принципами стали "красивое лучше уродливого" и "простота лучше сложности". Язык прошел через множество итераций, включая добавление декораторов, генераторов и type hints.',
            "impact": "Python стал одним из самых популярных языков программирования, особенно в области науки о данных, машинного обучения и веб-разработки. Используется в Google, Facebook, Netflix, Instagram.",
            "future": "Python продолжает доминировать в области ИИ и машинного обучения. Развивается в направлении повышения производительности (PyPy, Cython) и улучшения типизации (type hints).",
        },
        "projects": [
            {
                "name": "Django",
                "description": 'Высокоуровневый веб-фреймворк для Python, который поощряет быструю разработку и чистый, прагматичный дизайн. Django следует принципу "batteries included" и предоставляет встроенную ORM, систему аутентификации, админ-панель, маршрутизацию, middleware, кеширование, интернационализацию и многое другое. Фреймворк использует паттерн MVT (Model-View-Template) и включает в себя мощную систему миграций, автоматическую генерацию админки и встроенную защиту от CSRF, XSS и других атак. Django идеально подходит для создания сложных веб-приложений, CMS, e-commerce платформ и корпоративных решений с акцентом на безопасность и масштабируемость.',
                "github": "https://github.com/django/django",
                "code_example": """
from django.db import models
from django.shortcuts import render

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

def user_list(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})""",
            },
            {
                "name": "PyAudio",
                "description": "Мощная библиотека для работы со звуком в Python, основанная на PortAudio. PyAudio предоставляет простой и удобный интерфейс для записи и воспроизведения аудио, обработки звуковых сигналов в реальном времени и создания аудио-приложений. Библиотека поддерживает множество аудио форматов, различные устройства ввода/вывода, настройку параметров качества звука и работу с аудио потоками. PyAudio широко используется для создания музыкальных приложений, систем распознавания речи, аудио анализа, подкастов, стриминга и других проектов, связанных со звуком. Предоставляет кроссплатформенный API для работы с аудио на Windows, macOS и Linux.",
                "github": "https://github.com/intxcc/pyaudio_portaudio",
                "code_example": """
import pyaudio
import wave

chunk = 1024
format = pyaudio.paInt16
channels = 2
rate = 44100

p = pyaudio.PyAudio()
stream = p.open(format=format, channels=channels, rate=rate, input=True)
frames = stream.read(chunk)""",
            },
            {
                "name": "NumPy",
                "description": "Фундаментальная библиотека для научных вычислений в Python, предоставляющая мощные N-мерные массивы и инструменты для работы с ними. NumPy является основой для большинства научных библиотек Python, включая SciPy, Pandas, Matplotlib и scikit-learn. Библиотека обеспечивает высокую производительность благодаря реализации на C и оптимизированным алгоритмам линейной алгебры. NumPy включает в себя функции для математических операций, статистики, линейной алгебры, преобразований Фурье, генерации случайных чисел и работы с массивами. Широко используется в data science, машинном обучении, научных исследованиях, финансовом анализе и инженерных расчетах.",
                "github": "https://github.com/numpy/numpy",
                "code_example": """
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
matrix = np.random.rand(3, 3)

result = np.dot(matrix, arr)
print(result)""",
            },
            {
                "name": "FastAPI",
                "description": "Современный, быстрый веб-фреймворк для создания API с Python, основанный на Starlette и Pydantic. FastAPI предоставляет автоматическую генерацию OpenAPI документации, валидацию данных на основе type hints, асинхронную поддержку и высокую производительность, сравнимую с Node.js и Go. Фреймворк включает в себя встроенную поддержку WebSockets, GraphQL, OAuth2, JWT, CORS, dependency injection и тестирования. FastAPI идеально подходит для создания высокопроизводительных API, микросервисов, real-time приложений и интеграционных сервисов. Предоставляет отличный developer experience с автоматическими подсказками в IDE и подробной документацией.",
                "github": "https://github.com/tiangolo/fastapi",
                "code_example": """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users/")
async def create_user(user: User):
    return {"user": user}""",
            },
        ],
        "icon": "python",
    },
]


@app.route("/")
def index():
    """Главная страница"""
    return render_template("index.html", languages=LANGUAGES)


@app.route("/about")
def about():
    """Страница О нас"""
    return render_template("about.html")


@app.route("/<language_slug>")
def language_page(language_slug):
    """Страница языка"""
    language = next((lang for lang in LANGUAGES if lang["slug"] == language_slug), None)
    if not language:
        return "Язык не найден", 404
    return render_template("language.html", language=language)


@app.route("/<language_slug>/history")
def language_history(language_slug):
    """История языка"""
    language = next((lang for lang in LANGUAGES if lang["slug"] == language_slug), None)
    if not language:
        return "Язык не найден", 404
    return render_template("history.html", language=language)


@app.route("/<language_slug>/projects")
def language_projects(language_slug):
    """Проекты языка"""
    language = next((lang for lang in LANGUAGES if lang["slug"] == language_slug), None)
    if not language:
        return "Язык не найден", 404

    import copy

    language_copy = copy.deepcopy(language)
    for project in language_copy["projects"]:
        if "code_example" in project:
            highlighted = highlight_code(project["code_example"], language_slug)
            project["code_example"] = highlighted

    return render_template("projects.html", language=language_copy)


if __name__ == "__main__":
    app.run(host="::", port=8000, debug=False)
