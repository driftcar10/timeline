FROM python:3.11.0a4-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scripts .

CMD [ "python", "./app.py" ]