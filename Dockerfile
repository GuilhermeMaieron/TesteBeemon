FROM python:3.10-slim

WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     --no-install-recommends && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
