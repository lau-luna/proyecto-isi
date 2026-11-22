from flask_wtf import FlaskForm
from wtforms import SubmitField


class LogOutForm(FlaskForm):
    submit = SubmitField("Log out")
