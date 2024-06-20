from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://anastasiiakravets:@localhost/project_tracker"
app.config["SECRET_KEY"] = b'\xa6\xcbo-Z\xf6\xeb\xce\xb0\xbc\xf9"\xba\xad\xed\xe2\xa4L\x14\x1a\xde\x8eg@'

# How correctly add DB connection without cycle import?
db = SQLAlchemy(app)


class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=50))

    task = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    description = db.Column(db.String(length=50))
    completed = db.Column(db.Boolean, default=False)

    project = db.relationship("Project", back_populates="task")


@app.route("/")
def render_home():
    return render_template("index.html", projects=Project.query.all())


@app.route("/project/<project_id>")
def render_project(project_id):
    return render_template("project-page.html", project=Project.query.filter_by(project_id=project_id).first(),
                           tasks=Task.query.filter_by(project_id=project_id).all())


@app.route("/add/project", methods=["POST"])
def add_project():
    if request.form['project-title']:
        project = Project(title=request.form['project-title'])
        db.session.add(project)
        db.session.commit()
        flash("Project added successfully", "green")
    else:
        flash("Enter a title for your new project", "red")
    return redirect(url_for('render_home'))


@app.route("/add/task/<project_id>", methods=["POST"])
def add_task(project_id):
    if request.form['task-name']:
        task = Task(description=request.form['task-name'], project_id=project_id)
        db.session.add(task)
        db.session.commit()
        flash("Task added successfully", "green")
    else:
        flash("Enter a title for your new task", "red")
    return redirect(url_for('render_project', project_id=project_id))


@app.route("/delete/project/<project_id>", methods=["POST"])
def delete_project(project_id):
    Task.query.filter_by(project_id=project_id).delete()
    Project.query.filter_by(project_id=project_id).delete()
    db.session.commit()
    return redirect(url_for('render_home'))


@app.route("/delete/task/<task_id>", methods=["POST"])
def delete_task(task_id):
    tasks_to_delete = Task.query.filter_by(task_id=task_id).first()
    project_id = tasks_to_delete.project.project_id
    db.session.delete(tasks_to_delete)
    db.session.commit()
    return redirect(url_for('render_project', project_id=project_id))


@app.route("/back", methods=["POST"])
def back_home():
    return redirect(url_for('render_home'))


@app.route("/mark/task/<task_id>", methods=["POST"])
def mark_task(task_id):
    task_to_mark = Task.query.filter_by(task_id=task_id).first()
    project_id = task_to_mark.project.project_id
    task_to_mark.completed = True
    db.session.commit()
    flash("Task marked successfully", "green")
    return redirect(url_for('render_project', project_id=project_id))


app.run(debug=True, host="127.0.0.1", port=3000)
