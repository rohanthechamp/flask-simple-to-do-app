from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Float, DateTime, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from sqlalchemy import desc
from datetime import datetime
from zoneinfo import ZoneInfo
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///to_do_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Bootstrap5(app)


# ^ Creating DB database
class Base(DeclarativeBase):
    pass


# ^ Create SQLAlchemy instance
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# ^ Create a Table in Database
class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=True)
    date_added: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata"))
    )

    completed: Mapped[bool] = mapped_column(Boolean, default=False)


# * Step 6
# ^ Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


# ^ Creating a WTF - forms
class add_task(FlaskForm):
    task_name = StringField(
        "Task_Name", validators=[DataRequired(message="Write your task here")]
    )
    priority = SelectField(
        "Star",
        choices=[
            ("0", "0 ⭐️"),
            ("1", "1 ⭐️"),
            ("2", "2 ⭐️"),
            ("3", "3 ⭐️"),
            ("4", "4 ⭐️"),
            ("5", "5 ⭐️"),
            ("6", "6 ⭐️"),
            ("7", "7 ⭐️"),
            ("8", "8 ⭐️"),
            ("9", "9 ⭐️"),
            ("10", "10 ⭐️"),
        ],
        validators=[],
    )
    completed_y_n = BooleanField("Completed?")

    submit = SubmitField("Submit")


class update_task(FlaskForm):
    completed_y_n = BooleanField("Completed?")
    submit = SubmitField("Submit")


@app.route("/")
def home():
    result = db.session.execute(db.select(Task))

    all_tasks = result.scalars().all()
    db.session.commit()
    return render_template("index.html", my_task=all_tasks)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = add_task()

    if form.validate_on_submit():
        new_task = Task(
            task=form.task_name.data,
            priority=form.priority.data,
            completed=form.completed_y_n.data,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add.html", form=form)


@app.route("/update", methods=["GET", "POST"])
def update():
    form = update_task()
    task_id = request.args.get("id")
    tasks = db.get_or_404(Task, task_id)

    if form.validate_on_submit():
        tasks.completed = int(form.completed_y_n.data)

        db.session.commit()

        return redirect(url_for("home"))

    return render_template("update.html", form=form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    task_id = request.args.get("id")
    tasks = db.get_or_404(Task, task_id)
    db.session.delete(tasks)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
