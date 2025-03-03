from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint("groups", __name__)


@bp.route("/")
def index():
    """Show all the groups."""
    db = get_db()
    groups = db.execute(
        "SELECT g.group_id, g.group_name, g.group_description, g.group_id, ug.user_id"
        " FROM groups g JOIN users_groups ug ON g.group_id = ug.group_id"
    ).fetchall()
    return render_template("groups/index.html", groups=groups)


def get_group(group_id, check_creator=True):
    """Get a group and its creator by id.

    Checks that the id exists and optionally that the current user is
    the creator.

    :param id: id of group to get
    :param check_author: require the current user to be the creator
    :return: the group with creator information
    :raise 404: if a group with the given id doesn't exist
    :raise 403: if the current user isn't the creator
    """
    group = (
        get_db()
        .execute(
            "SELECT g.group_id, g.group_name, g.group_description, ug.user_id, u.username"
            " FROM groups g JOIN users_groups ug ON g.group_id = ug.group_id"
            " JOIN users u ON ug.user_id = u.user_id"
            " WHERE g.group_id = ?",
            (group_id,),
        )
        .fetchone()
    )

    if group is None:
        abort(404, f"Group id {group_id} doesn't exist.")

    if check_creator and group["ug.user_id"] != g.users["user_id"]:
        abort(403)

    return group


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        group_name = request.form["group_name"]
        group_description = request.form["group_description"]
        error = None

        if not group_name:
            error = "Group name is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO groups (group_name, group_description) VALUES (?, ?)",
                (group_name, group_description),
                "INSERT INTO users_groups (user_id, group_id, group_creator) VALUES (?, ?, ?)",
                (g.users['user_id'], g.groups['group_id'], 'Y')
            )
            db.commit()
            return redirect(url_for("groups.index"))

    return render_template("groups/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
