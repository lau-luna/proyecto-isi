from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class AddQuestionForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    category = SelectField("Category", coerce=int, validators=[DataRequired()])
    tags = StringField("Tags", validators=[])
    body = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Ask question")
