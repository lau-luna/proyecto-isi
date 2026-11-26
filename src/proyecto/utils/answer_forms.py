from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AnswerForm(FlaskForm):
    body = TextAreaField(
        "Your answer",
        validators=[DataRequired(message="Please write an answer.")],
    )
    submit = SubmitField("Post answer")
