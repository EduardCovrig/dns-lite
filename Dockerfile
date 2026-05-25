FROM python:3.9-slim
WORKDIR /app
COPY server.py .
COPY server_db_8719.txt .
EXPOSE 8719
CMD ["python", "server.py", "8719"]
