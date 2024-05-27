# Stage 1
FROM python:3-slim-buster AS builder

WORKDIR /flask-app

COPY . /flask-app/

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/flask-app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]