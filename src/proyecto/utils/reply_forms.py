from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class ReplyForm(FlaskForm):
    body = TextAreaField(
        "Your reply",
        validators=[DataRequired(message="Please write a reply.")],
    )
    submit = SubmitField("Reply")
