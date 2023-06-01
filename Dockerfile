FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]  

#64090500432
#64090500437