FROM python:3.7-alpine
WORKDIR /PPD_app

ENV FLASK_APP files_app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8881

COPY ./PPD_app /PPD_app

RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]

