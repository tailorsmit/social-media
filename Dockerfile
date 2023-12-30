FROM python:3.9

WORKDIR /home/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn","assignment1.wsgi","-b","0.0.0.0:8000"]

