# nastyatonkova/hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

Backend Development Faculty Sprint 6 Learning Project [Yandex.Practicum](https://practicum.yandex.ru/backend-developer)

## Tech-Stack:
- Python
- Django
- Autotests (s. directory `tests/`).

---
## How to run the project:

Clone repository to you PC and go to it with your terminal using CD command:

```bash
git clone https://github.com/chaplinskiy/hw05_final.git
```

Create and activate virtual environment:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
python3 -m pip install --upgrade pip
```

Install dependencies from the file requirements.txt:

```bash
pip install -r requirements.txt
```

Make migration:

```bash
cd yatube/ && python3 manage.py migrate
```

Run the project:

```bash
python3 manage.py runserver
```

Run `pytest`:

*from main folder with active virtual environment*
```bash
pytest
```

### Template file for env
см.
```bash
.env.template
```


## Другие проекты автора:
https://github.com/nastyatonkova/
