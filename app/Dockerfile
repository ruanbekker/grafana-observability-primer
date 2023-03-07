FROM python:3.8-slim
WORKDIR /src
RUN apt update && apt install python3-dev build-essential -y && pip install -U pip && pip install --upgrade setuptools && pip install wheel
COPY requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt
COPY server.py /src/server.py
#CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:80", "--capture-output", "--access-logfile", "'-'", "--error-logfile", "'-'"]
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:5000"]
#CMD [ "python", "server.py" ]