FROM python:3.9

WORKDIR /home

COPY scraper.py .

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["python", "./scraper.py"]