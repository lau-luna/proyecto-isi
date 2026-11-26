import pytest
from test_answer import create_question
from test_auth import create_test_user

from proyecto.models.HumanAuthorFactory import HumanAuthorFactory
from proyecto.models.Question import Question
from proyecto.models.Tag import Tag


@pytest.fixture
def ranked(session):
    """Three questions: 'Popular' (+2), 'Newest' (0, created last), 'Disliked' (-1)."""
    asker = create_test_user(session)
    juan = create_test_user(session, username="juan", email="juan@example.com")
    popular = create_question(session, asker)
    popular.title = "Popular question"
    disliked = Question(
        title="Disliked question",
        category_id=popular.category_id,
        body="Body",
        user_id=asker.id,
        tags=[Tag("vim")],
    )
    newest = Question(
        title="Newest question",
        category_id=popular.category_id,
        body="Body",
        user_id=asker.id,
        tags=[],
    )
    session.add_all([disliked, newest])
    session.commit()
    popular.tags.append(disliked.tags[0])
    newest.tags.append(disliked.tags[0])
    popular.upvote(asker)
    popular.upvote(juan)
    disliked.downvote(juan)
    session.commit()
    return popular, newest, disliked


def positions(html, *titles):
    return [html.index(title.encode()) for title in titles]


def assert_in_order(html, *titles):
    found = positions(html, *titles)
    assert found == sorted(found), f"expected order {titles}"


ORDER_BY_SCORE = ("Popular question", "Newest question", "Disliked question")


@pytest.mark.parametrize("url", ["/questions", "/questions?q=question"])
def test_lists_are_ordered_by_score(client, ranked, url):
    assert_in_order(client.get(url).data, *ORDER_BY_SCORE)


def test_category_page_is_ordered_by_score_by_default(client, ranked):
    popular, _, _ = ranked

    response = client.get(f"/category/{popular.category_id}")

    assert_in_order(response.data, *ORDER_BY_SCORE)
    assert b'id="selected-sort">Best Score<' in response.data


def test_tag_page_is_ordered_by_score_by_default(client, ranked):
    _, _, disliked = ranked

    response = client.get(f"/tag/{disliked.tags[0].id}")

    assert_in_order(response.data, *ORDER_BY_SCORE)


def test_category_page_can_sort_by_newest_and_oldest(client, ranked):
    popular, _, _ = ranked
    url = f"/category/{popular.category_id}"

    newest = client.get(f"{url}?sort=newest").data
    oldest = client.get(f"{url}?sort=oldest").data

    assert_in_order(newest, "Newest question", "Disliked question", "Popular question")
    assert b'id="selected-sort">Newest<' in newest
    assert_in_order(oldest, "Popular question", "Disliked question", "Newest question")


def test_unknown_sort_falls_back_to_score(client, ranked):
    popular, _, _ = ranked

    response = client.get(f"/category/{popular.category_id}?sort=bogus")

    assert response.status_code == 200
    assert_in_order(response.data, *ORDER_BY_SCORE)


def test_order_changes_after_voting(client, ranked, session):
    popular, newest, _ = ranked
    juan = newest.author  # any user different from the existing voters works
    ana = create_test_user(session, username="ana", email="ana@example.com")
    for voter in (juan, ana):
        newest.upvote(voter)
    newest.upvote(create_test_user(session, username="bo", email="bo@example.com"))
    session.commit()

    assert_in_order(
        client.get("/questions").data, "Newest question", "Popular question"
    )


def test_answers_are_ordered_by_score_on_the_detail(client, session):
    asker = create_test_user(session)
    juan = create_test_user(session, username="juan", email="juan@example.com")
    question = create_question(session, asker)
    factory = HumanAuthorFactory(asker)
    first = question.add_answer("First answer", factory)
    second = question.add_answer("Second answer", factory)
    third = question.add_answer("Third answer", factory)
    question.add_answer("Fourth answer", factory)
    session.commit()
    third.upvote(asker)
    third.upvote(juan)
    first.downvote(juan)
    session.commit()

    response = client.get(f"/questions/{question.id}")

    # Most voted first; answers with the same score keep their age order.
    assert_in_order(
        response.data, "Third answer", "Second answer", "Fourth answer", "First answer"
    )
    assert [a.body for a in question.answers_by_score] == [
        "Third answer",
        "Second answer",
        "Fourth answer",
        "First answer",
    ]
    assert second.score == 0


def test_index_is_ordered_by_newest(client, ranked):
    assert_in_order(
        client.get("/").data,
        "Newest question",
        "Disliked question",
        "Popular question",
    )
