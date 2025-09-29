FROM python:3.11
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

#RUN python3 manage.py migrate
#
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]