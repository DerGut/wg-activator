FROM python:3.6-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./wait-for-grid.sh", "python", "wg-updater.py"]
