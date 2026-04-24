FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
