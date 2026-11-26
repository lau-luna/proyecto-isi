from argon2 import PasswordHasher
from sqlalchemy import inspect, select

from proyecto.extensions import db
from proyecto.models.Administrator import Administrator
from proyecto.models.Answer import Answer
from proyecto.models.Category import Category
from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Moderator import Moderator
from proyecto.models.Post import Post
from proyecto.models.Question import Question
from proyecto.models.RegularUser import RegularUser
from proyecto.models.Tag import Tag
from proyecto.models.User import User

_hasher = PasswordHasher()


def seed_categories():
    if not inspect(db.engine).has_table(Category.__tablename__):
        return

    categories = [
        "Technology",
        "Programming",
        "Science",
        "Mathematics",
        "History",
        "Geography",
        "Literature",
        "Arts & Culture",
        "Music",
        "Movies & TV",
        "Video Games",
        "Sports",
        "Health & Fitness",
        "Food & Cooking",
        "Travel",
        "Education",
        "Career & Work",
        "Personal Finance",
        "Home & Garden",
        "Lifestyle",
        "Other",
    ]

    for cat_name in categories:
        if db.session.scalar(select(Category).where(Category.name == cat_name)) is None:
            db.session.add(Category(cat_name))

    db.session.commit()


def seed_users():
    if not inspect(db.engine).has_table(User.__tablename__):
        return
    if db.session.scalar(select(User)) is not None:
        return

    pw = _hasher.hash("password123")
    for name in ("alice", "bob", "carol"):
        db.session.add(
            RegularUser(username=name, email=f"{name}@example.com", password_hash=pw)
        )
    db.session.add(Moderator(username="mod", email="mod@example.com", password_hash=pw))
    db.session.add(
        Administrator(username="admin", email="admin@example.com", password_hash=pw)
    )
    db.session.commit()


def seed_tags():
    if not inspect(db.engine).has_table(Tag.__tablename__):
        return
    if db.session.scalar(select(Tag)) is not None:
        return
    for name in ("python", "vim", "linux", "help", "humor"):
        db.session.add(Tag(name))
    db.session.commit()


def seed_questions():
    if not inspect(db.engine).has_table(Question.__tablename__):
        return
    if db.session.scalar(select(Question)) is not None:
        return
    cats = {c.name: c for c in db.session.scalars(select(Category)).all()}
    users = db.session.scalars(select(User)).all()
    tags = {t.name: t for t in db.session.scalars(select(Tag)).all()}

    data = [
        (
            "How do I exit vim?",
            "I opened vim by accident and I'm stuck. :q! didn't work, what do I do?",
            "Technology",
            ["vim", "linux", "help"],
        ),
        (
            "Best way to learn Python?",
            "I'm a beginner, where should I start?",
            "Programming",
            ["python"],
        ),
        ("Why is the sky blue?", "Simple physics question.", "Science", []),
        (
            "Tabs or spaces?",
            "Settle this once and for all.",
            "Programming",
            ["python", "humor"],
        ),
        ("Best travel destination 2026?", "Looking for ideas.", "Travel", []),
        (
            "How to cook pasta al dente?",
            "Mine always comes out mushy.",
            "Food & Cooking",
            [],
        ),
    ]

    for i, (title, body, cat, tagnames) in enumerate(data):
        author = users[i % len(users)]
        q = Question(
            title=title,
            category_id=cats[cat].id,
            body=body,
            user_id=author.id,
            tags=[tags[t] for t in tagnames if t in tags],
        )
        db.session.add(q)
    db.session.commit()


def seed_answers():
    if not inspect(db.engine).has_table(Answer.__tablename__):
        return
    if db.session.scalar(select(Answer)) is not None:
        return
    users = db.session.scalars(select(User)).all()
    questions = db.session.scalars(select(Question)).all()
    for qi, q in enumerate(questions):
        responder = users[(qi + 1) % len(users)]  # never answer your own question
        q.add_answer(
            body="Great question, here's my take.",
            factory=HumanAuthorFactory(responder),
        )
        if qi == 0:
            expert = users[(qi + 2) % len(users)]
            correct = q.add_answer(
                body="Type :q! and press Enter. You're welcome.",
                factory=HumanAuthorFactory(expert),
            )
            q.accept_answer(correct, q.author)
    db.session.commit()


def seed_votes():
    if not inspect(db.engine).has_table(Post.__tablename__):
        return
    posts = db.session.scalars(select(Post)).all()
    users = db.session.scalars(select(User)).all()
    for post in posts:
        author_id = (
            post.user_id if isinstance(post, Question) else post.author_record.user_id
        )
        for vi, voter in enumerate(users):
            if voter.id == author_id or post.vote_of(voter) is not None:
                continue
            if vi % 3 == 2:
                post.downvote(voter)
            else:
                post.upvote(voter)
    db.session.commit()


def seed_all():
    seed_categories()
    seed_users()
    seed_tags()
    seed_questions()
    seed_answers()
    seed_votes()
