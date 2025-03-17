FROM python@sha256:28b8a72c4e0704dd2048b79830e692e94ac2d43d30c914d54def6abf74448a4e
WORKDIR /secretary
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY src ./src
ENTRYPOINT ["python3", "src/bot.py"]
