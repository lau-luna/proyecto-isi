"""Role-based authorization (issue #5).

Permissions are checked in one place, the role_required decorator, instead
of repeating "if" checks inside every view.

How roles map to permissions:
- Asking, answering and voting: any logged-in user
  -> @role_required(RegularUser, Moderator)
- Deleting posts: Moderator or Administrator -> @role_required(Moderator)
- Managing users (including changing roles): Administrator only
  -> @role_required(Administrator)

Administrator is a subclass of Moderator, so isinstance(admin, Moderator) is
True: allowing Moderator automatically allows Administrator too.

The current user (g.user) is loaded from the database at the start of every
request (see load_logged_in_user in create_app), so a role change takes
effect on the user's next request.
"""

from functools import wraps

from flask import abort, g, redirect, url_for

from proyecto.models.User import User


def user_has_role(user: User | None, *allowed_roles: type[User]) -> bool:
    """Return True if the user is an instance of any of the allowed role classes.

    A visitor without a session (user is None) has no role.
    """
    if user is None:
        return False
    return isinstance(user, allowed_roles)


def role_required(*allowed_roles: type[User]):
    """Allow the view only to users of the given role classes.

    - Visitor without a session: redirect to the login page.
    - Logged-in user with another role: 403 Forbidden.

    Usage:
        @bp.route("/posts/<int:post_id>/delete", methods=["POST"])
        @role_required(Moderator)
        def delete_post(post_id): ...
    """

    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for("user.login"))
            if not user_has_role(g.user, *allowed_roles):
                abort(403)
            return view(**kwargs)

        return wrapped_view

    return decorator
