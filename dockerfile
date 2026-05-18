FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# зависимости Python
COPY requrements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requrements.txt

# копируем проект
COPY . /app/

# запуск (пока для dev)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]