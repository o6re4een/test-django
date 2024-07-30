FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN pip install --upgrade pip && pip install -r requirements.txt



EXPOSE 8000
COPY . /app/


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]