FROM python:3.11.2-bullseye

EXPOSE 8080

WORKDIR /phoenixc2

COPY . . 

RUN python --version

RUN pip install poetry --disable-pip-version-check

RUN poetry install

RUN apt update && apt install -y golang-go

ENTRYPOINT ["poetry", "run"]

CMD ["phserver", "--host", "0.0.0.0", "--port", "$PORT"]
