# Social media project

## Installation Steps
    git clone https://github.com/tailorsmit/social-media.git
    cd social-media
    python -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements.txt

## Configuration

 1. Open file assignment1/settings.py and configure Database (optional).
 2. Open terminal in Root directory of the project.
 3. export a variable for SECRET_KEY (Run `export SECRET_KEY='your_secret_key'`).
 4. Run `python manage.py makemigrations && python manage.py migrate` to create and apply migration to your database.
 
## Run Server

### Without Docker
    gunicorn assignment1.wsgi -b 0.0.0.0:8000
### Using Docker

    docker build -t assignment . --platform linux/amd64
    docker run -p 8000:8000 --platform linux/amd64 --env SECRET_KEY=$SECRET_KEY -v ./db.sqlite3:/home/app/db.sqlite3 assignment

---
#### Note: 

 - Here, while executing docker run command we have user -v flag to
   mount volume so that we will not lose the db information residing
   in container. also, `$SECRET_KEY` should be same as the one we have
   exported in **Configuration** section.
