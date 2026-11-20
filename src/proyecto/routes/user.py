from argon2 import PasswordHasher
from flask import Blueprint, render_template, request
from sqlalchemy import select

from proyecto.extensions import db
from proyecto.models.User import User

bp = Blueprint("user", __name__, template_folder="templates")

pass_hasher = PasswordHasher()


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

    user = User(username=username, email=email, password_hash=password_hash)

    db.session.add(user)
    db.session.commit()


@bp.route("/user/register", methods=["GET", "POST"])
def register():
    result_valid_register = {}

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]

        result_valid_register = valid_register(
            username, email, password, password_confirm
        )

        if result_valid_register is None:
            register_user(username, email, password)
        else:
            print(result_valid_register)

    return render_template("user/register.html", errors=result_valid_register)
