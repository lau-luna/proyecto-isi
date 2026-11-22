import re
from functools import wraps

from argon2 import PasswordHasher
from flask import Blueprint, g, redirect, render_template, request, session, url_for
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.RegularUser import RegularUser
from proyecto.models.User import User
from proyecto.utils.user_forms import RegisterForm, LoginForm

bp = Blueprint("user", __name__, template_folder="templates")

pass_hasher = PasswordHasher()
email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_register(username, email, password, password_confirm):
    errors = {}

    fields = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password_confirm,
    }
    for field, value in fields.items():
        if not value:
            errors[field] = "This field is required"

    if errors:
        return errors

    if not email_pattern.fullmatch(email):
        errors["email"] = "Enter a valid email address"
        return errors

    if password != password_confirm:
        errors["password"] = "Passwords do not match"
        return errors

    user_from_db = db.session.scalar(select(User).where(User.email == email))

    if user_from_db is not None:
        errors["email"] = "Email already exists"
        return errors

    user_from_db = db.session.scalar(select(User).where(User.username == username))

    if user_from_db is not None:
        errors["username"] = "Username is already taken"
        return errors

    return None


def register_user(username, email, password):
    password_hash = pass_hasher.hash(password)

    user = RegularUser(username=username, email=email, password_hash=password_hash)

    db.session.add(user)
    db.session.commit()


@bp.route("/user/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data
        password_confirm = form.password_confirm.data

        errors = valid_register(username, email, password, password_confirm)
        if errors is None:
            register_user(username, email, password)
            return (
                render_template(
                    "user/login.html",
                    form=LoginForm(formdata=None, email=email),
                    email=email,
                ),
                200,
            )

        for field, message in errors.items():
            getattr(form, field).errors.append(message)

    return render_template("user/register.html", form=form), (
        400 if request.method == "POST" else 200
    )


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("user.login"))
        return view(**kwargs)

    return wrapped_view


@bp.route("/user/login", methods=["GET", "POST"])
def login():
    error = None
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data 

        user = db.session.scalar(select(User).where(User.email == email))

        if user is None or not user.verify_password(password):
            error = "Invalid email or password"
            return render_template("user/login.html", form=form, error=error), 401

        session.clear()
        session["user_id"] = user.id
        return redirect(url_for("index"))

    return render_template("user/login.html", form=form, error=error)


@bp.route("/user/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))
