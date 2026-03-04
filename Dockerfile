FROM python:3.13.7
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["waitress-serve", "--bind", "0.0.0.0:5000", "main:app"]