from flask import render_template, request, redirect, session, url_for, flash
from . import app, db
from app import *
from flask_wtf import FlaskForm 
from wtforms import TextAreaField, StringField, BooleanField, PasswordField, SelectField, validators, Form
from passlib.hash import pbkdf2_sha256


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('Remember me', default=False)
 
class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [  
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class TaskForm(FlaskForm):
    title = StringField('Username', [validators.DataRequired(),validators.Length(max=100)])
    desc = TextAreaField('Description', [validators.DataRequired(), validators.Length(min=1, max=500)])
    done = BooleanField('Done', default=False)
    idGroup = SelectField('Group', coerce=int, validate_choice=False)

class GroupForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired(),validators.Length(max=100)])
    # color = StringField('Color')
@app.route("/")
def home():
    return render_template("public/home.html")

@app.route("/tasks")
def tasks():
    if "logged_in" in session:
        if session["logged_in"] is not None:
            user = User.query.filter_by(username=session["logged_in"]).first()
            idUser = user.id
            tasks = Task.query.filter_by(idUser=idUser, done=False).all()
            groups = Group.query.filter_by(idUser=idUser).all()
            group_list = []
            for group in groups:
                if any(t.done == False for t in group.tasks):
                    group_list.append(group)
        return render_template("public/tasks.html", tasks=tasks, groups=group_list)
    else:
        flash('You need to be logged in', 'danger')
        return redirect(url_for('login'))
    return render_template("public/tasks.html")

@app.route("/history")
def history():
    if "logged_in" in session:
        if session["logged_in"] is not None:
            user = User.query.filter_by(username=session["logged_in"]).first()
            idUser = user.id
            tasks = Task.query.filter_by(idUser=idUser, done=True).all()
            groups = Group.query.filter_by(idUser=idUser).all()
            print(tasks)
        return render_template("public/history.html", tasks=tasks, groups=groups)
    else:
        flash('You need to be logged in', 'danger')
        return redirect(url_for('login'))
    return render_template("public/history.html")

@app.route("/create_task", methods=["GET", "POST"])
def create():
    form = TaskForm()
    user = User.query.filter_by(username=session["logged_in"]).first()
    group = Group.query.filter_by(name="No group").filter_by(idUser=user.id).first()
    form = TaskForm(idGroup=group.id)
    if request.method == "GET":
        form.idGroup.choices = [(g.id, g.name) for g in Group.query.filter_by(idUser=user.id).order_by('name')]
        return render_template('public/create_task.html', form=form)
    if form.validate_on_submit():
        title = form.title.data
        desc = form.desc.data
        done = form.done.data
        idGroup = form.idGroup.data
        user = User.query.filter_by(username=session["logged_in"]).first()
        new_task = Task(title=title, desc=desc, done=done, idUser=user.id, idGroup=idGroup)
        db.session.add(new_task)
        db.session.commit()

        flash(f'Task {title} created!', 'primary')
        return redirect(url_for('tasks'))
    return render_template('public/create_task.html', form=form)

@app.route("/create_task/<string:id>", methods=["GET", "POST"])
def create_task(id):
    form = TaskForm()
    user = User.query.filter_by(username=session["logged_in"]).first()
    group = Group.query.filter_by(id=id).filter_by(idUser=user.id).first()
    form = TaskForm(idGroup=group.id)
    if request.method == "GET":
        form.idGroup.choices = [(g.id, g.name) for g in Group.query.filter_by(idUser=user.id).order_by('name')]
        return render_template('public/create_task.html', form=form)
    if form.validate_on_submit():
        title = form.title.data
        desc = form.desc.data
        done = form.done.data
        idGroup = form.idGroup.data
        user = User.query.filter_by(username=session["logged_in"]).first()
        new_task = Task(title=title, desc=desc, done=done, idUser=user.id, idGroup=idGroup)
        db.session.add(new_task)
        db.session.commit()

        flash(f'Task {title} created!', 'primary')
        return redirect(url_for('tasks'))
    return render_template('public/create_task.html', form=form)


@app.route('/done_task/<string:id>')
def done(id):
    done_task = Task.query.filter_by(id=id).first()
    done_task.done = True
    db.session.commit()

    flash('Task finished', 'primary')
    return redirect(url_for('tasks'))

@app.route('/undone_task/<string:id>')
def undone(id):
    undone_task = Task.query.filter_by(id=id).first()
    undone_task.done = False
    db.session.commit()

    flash('Task unfinished', 'primary')
    return redirect(url_for('history'))


@app.route('/delete_task/<string:id>')
def delete(id):
    delete_task = Task.query.filter_by(id=id).first()
    db.session.delete(delete_task)
    db.session.commit()

    flash('Task Deleted', 'primary')
    return redirect(url_for('history'))

@app.route('/edit_task/<string:id>', methods=['GET', 'POST'])
def edit(id):
    edit_task = Task.query.filter_by(id=id).first()
    group = Group.query.filter_by(id=edit_task.idGroup).first()
    form = TaskForm(idGroup=group.id)
    if request.method == "GET":
        form.title.data = edit_task.title
        form.desc.data = edit_task.desc
        form.done.data = edit_task.done
        user = User.query.filter_by(username=session["logged_in"]).first()
        form.idGroup.choices = [(g.id, g.name) for g in Group.query.filter_by(idUser=user.id).order_by('name')]
        return render_template('public/edit_task.html', form=form)

    elif form.validate_on_submit() and request.method == "POST":
        edit_task.title = form.title.data
        edit_task.desc = form.desc.data
        edit_task.done = form.done.data
        edit_task.idGroup = form.idGroup.data
        db.session.commit()
        print("Edit: " + edit_task.desc)
        print("Edit: " + form.desc.data)
        flash('Task edited', 'primary')
        return redirect(url_for('tasks'))

    return redirect(url_for('tasks'))

 
@app.route('/create_group', methods=["GET", "POST"])
def create_group():
    form = GroupForm()
    print("in new form:")
    print(form)
    if form.validate_on_submit():
        name = form.name.data
        user = User.query.filter_by(username=session["logged_in"]).first()
        new_group = Group(name=name, idUser=user.id)
        db.session.add(new_group)
        db.session.commit()
        flash(f'Group {name} created!', 'primary')
        return redirect(url_for('tasks'))
    return render_template('public/create_group.html', form=form)

@app.route('/edit_group/<string:id>', methods=['GET', 'POST'])
def edit_group(id):
    edit_group = Group.query.filter_by(id=id).first()
    form = GroupForm()
    if request.method == "GET":
        form.name.data = edit_group.name
        return render_template('public/edit_group.html', form=form, id=id)

    elif form.validate_on_submit() and request.method == "POST":
        edit_group.name = form.name.data
        db.session.commit()
        flash('Group edited', 'primary')
        return redirect(url_for('tasks'))
    return redirect(url_for('tasks'))

@app.route('/delete_group/<string:id>')
def delete_group(id):
    user = User.query.filter_by(username=session["logged_in"]).first()
    tasks = Task.query.filter_by(idGroup=id).filter_by(idUser=user.id).all()
    default_group_id = Group.query.filter_by(idUser=user.id).filter_by(name="No group").first().id
    for t in tasks:
        t.idGroup = default_group_id
    delete_group = Group.query.filter_by(id=id).first()
    if delete_group.id == default_group_id:
        return redirect(url_for('tasks'))
    db.session.delete(delete_group)
    db.session.commit()

    flash('Group Deleted', 'primary')
    return redirect(url_for('tasks'))

@app.route("/") 
def index():
    return render_template("public/tasks.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        users = User.query.all()
        for user in users:
            if form.username.data.lower() == user.username:
                flash(f'Username already taken', 'danger')
                return render_template('public/signup.html', form=form)
            
        hashed_password = pbkdf2_sha256.hash(form.password.data)
        username = form.username.data.lower()
        password = form.password.data
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        user_found = User.query.filter_by(username=username).first()
        new_group = Group(name="No group", idUser = user_found.id)

        db.session.add(new_group)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'primary')
        print("we got this new user: " + username)
        return redirect(url_for('login'))
    return render_template('public/signup.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.username.data)
    print(form.password.data)
    if form.validate_on_submit():
        print("user validated")
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is not None:
            h = user.password
            if pbkdf2_sha256.verify(password, h):
                flash('Logged in as ' + username, 'primary')
                session["logged_in"] = username
                if form.remember_me.data == True:
                    session["USERNAME"] = username

                return redirect(url_for('tasks'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            print("username doesn't exist")
            flash('Login Unsuccessful. Please check username and password', 'danger')
        return render_template('public/login.html', form=form)
    return render_template('public/login.html', form=form)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    # session.pop("USERNAME", None)
    flash("Logout succesful!", 'primary')
    return redirect(url_for("login"))

# @app.route("/test")
# def test():
#     print(session["USERNAME"])
#     print(session)
#     print(session["logged_in"])
#     task = Task.query.all()
#     print(task)
#     session.pop("logged_in", None)
#     session.pop("USERNAME", None)
#     session.clear()
#     return "test"