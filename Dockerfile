FROM python:3.8.1
COPY . /transaction_server
WORKDIR /transaction_server
ENV PYTHONPATH=/transaction_server
VOLUME /transaction_server/transactionsDB
RUN pip install -r requirements.txt
CMD  ["python", "main.py", "-c", "config.yml"]
