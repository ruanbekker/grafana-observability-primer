FROM python:3.8-alpine
WORKDIR /src
COPY requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt
COPY server.py /src/server.py
#CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:80", "--capture-output", "--access-logfile", "'-'", "--error-logfile", "'-'"]
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:5000"]