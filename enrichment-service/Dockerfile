FROM python:3.9

WORKDIR /service

COPY ./requirements.txt /service/requirements.txt

RUN pip install --upgrade -r /service/requirements.txt

COPY ./app /service/app

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "trace"]
