FROM python:3.9-slim
WORKDIR /app
COPY server.py .
EXPOSE 8719
CMD ["python", "server.py", "8719"]
