FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ ./

LABEL author=lorpaxx@yandex.ru version=1.0.0

CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0:8000" ]
