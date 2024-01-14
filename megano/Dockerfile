FROM python:3.9.13

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.7.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install
RUN cd /app && poetry install

COPY diploma-frontend-0.6.tar.gz /app/

RUN pip install diploma-frontend-0.6.tar.gz
COPY . .`

RUN pip install gunicorn

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]