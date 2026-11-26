from flask_wtf import FlaskForm
from wtforms import SubmitField


class AcceptAnswerForm(FlaskForm):
    """Empty form: it only carries the CSRF token of the accept button."""

    submit = SubmitField("Accept")
