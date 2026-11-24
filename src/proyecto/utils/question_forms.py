from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class AddQuestionForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Please enter a valid title."),
            Length(max=255),
        ],
    )
    category = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired(message="Please select a category.")],
    )
    tags = StringField("Tags")
    body = TextAreaField(
        "Description",
        validators=[DataRequired(message="Please enter a valid body.")],
    )
    submit = SubmitField("Ask question")
