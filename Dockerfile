FROM python:3.13.7

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# Слушаем все интерфейсы, чтобы хост мог подключиться
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "main:app"]