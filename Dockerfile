FROM python:3.7.6
COPY . /transaction_server
ENV HOST=0.0.0.0
WORKDIR /transaction_server
VOLUME /transaction_server/transactionsDB
RUN pip install -r requirements.txt
RUN ln -sf /dev/stdout /var/log/transactions.log
CMD  ["python", "main.py"]
