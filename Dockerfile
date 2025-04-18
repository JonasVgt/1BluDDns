FROM python:3.11-slim

COPY . /app
WORKDIR /app


RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python", "./app/main.py" ]