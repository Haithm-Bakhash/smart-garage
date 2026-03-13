FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# The -u flag tells Python to print logs immediately to the terminal
CMD ["python", "-u", "main.py"]