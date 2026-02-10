# Async-sdamgia-api

Неофициальный асинхронный Python-клиент для работы с платформой `sdamgia.ru`: получение задач, поиск, работа с категориями и тестами, генерация PDF и OCR-поиск по изображению.

## Что умеет

- получать задачу по `id` (`get_problem_by_id`)
- искать задачи по тексту (`search`)
- получать задачи теста по `testid` (`get_test_by_id`)
- получать задачи категории (`get_category_by_id`)
- загружать каталог тем и категорий (`get_catalog`)
- генерировать тест (`generate_test`)
- получать ссылку на PDF теста (`generate_pdf`)
- искать задачи по изображению через OCR (`search_by_img`)

Поддерживаемые предметы (коды):
`math`, `mathb`, `phys`, `inf`, `rus`, `bio`, `en`, `chem`, `geo`, `soc`, `de`, `fr`, `lit`, `sp`, `hist`.

## Установка

Требования:
- Python `3.12+`

```bash
pip install sdamgia-api
```

Для разработки:

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Быстрый старт

```python
import asyncio
from sdamgia import SdamGIA


async def main() -> None:
    async with SdamGIA() as api:
        problem = await api.get_problem_by_id("math", "1001")
        print(problem["id"], problem["answer"])


asyncio.run(main())
```

## Примеры API

```python
# Поиск задач
ids = await api.search("math", "Найдите количество")

# Каталог предмета
topics = await api.get_catalog("math")

# Генерация теста и PDF
new_test_id = await api.generate_test("math", {"full": 1})
pdf_url = await api.generate_pdf("math", new_test_id, pdf="h")
```

Рендер задачи в изображение (`get_problem_by_id`) поддерживает `img`:
- `pyppeteer`
- `grabzit`
- `html2img`

## OCR-поиск по изображению

Метод `search_by_img` использует `pytesseract`.

1. Установите Python-пакет (если не установлен):

```bash
pip install pytesseract
```

2. Установите `Tesseract-OCR` в ОС и при необходимости укажите путь:

```python
api.tesseract_src = "/usr/bin/tesseract"
# Windows пример: C:/Program Files/Tesseract-OCR/tesseract.exe
```

3. Запустите поиск:

```python
ids = await api.search_by_img("rus", "Image.jpg")
```

## Тесты

В проекте используется live-контур (реальные запросы к `*.sdamgia.ru`):

```bash
pytest -m live -q
```

Важно:
- тесты зависят от сети и доступности внешнего сайта
- структура внешнего HTML может меняться без предупреждения
- OCR ветка в тестах замокана (без обязательной установки Tesseract)

## CI

GitHub Actions запускает live-тесты на `push` и `pull_request` для Python `3.12` и `3.13`.
При падении сохраняются логи (`junit` + `live.log`) как artifacts.

## Для AI-агентов

В репозитории есть файл `AGENTS.md` с обязательными правилами для агентной разработки:

- кодстайл и требования к Python-коду
- правила по docstring (Google-style)
- требования к тестам
- список доступных skills и когда их применять

Если вы используете Codex/агента, начинайте с чтения `AGENTS.md`.

## Лицензия

MIT
