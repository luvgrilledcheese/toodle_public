# toodle
#### A simple task manager (todo list) made with Flask and SQLAlchemy
##### Try it out: http://luvgrilledcheese.pythonanywhere.com/
### How to use locally
```
$ pip install -r requirements.txt
$ export FLASK_APP=app

$ python
>> from app import db
>> db.create_all()
>> exit()

$ flask run
```
