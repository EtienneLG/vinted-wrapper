## Setup the webapp

This application uses the framework django. To install:
```
$ pip install Django
```
To setup the db, go in the `/alsovinted` directory and run:
```
$ python manage.py makemigrations
$ python manage.py migrate
```
To run the app:
```
$ python manage.py runserver
```
The app will be available at http://127.0.0.1:8000/
