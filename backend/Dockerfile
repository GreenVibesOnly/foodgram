FROM python:3.9-slim
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY requirements/requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]