"""
conftest.py - Shared fixtures for all tests
"""

import pytest

from apps.blog.models import Post
from apps.users.models import Author


@pytest.fixture
def author(db):
    return Author.objects.create(
        name="Yash",
        email="yash@example.com",
        bio="Test author",
    )


@pytest.fixture
def second_author(db):
    return Author.objects.create(
        name="Alice",
        email="alice@example.com",
        bio="Second author",
    )


@pytest.fixture
def published_post(db, author):
    return Post.objects.create(
        title="Published Post",
        content="Some published content.",
        author=author,
        status=Post.Status.PUBLISHED,
    )


@pytest.fixture
def draft_post(db, author):
    return Post.objects.create(
        title="Draft Post",
        content="Some draft content.",
        author=author,
        status=Post.Status.DRAFT,
    )


def gql(client, query, variables=None):
    """Helper to fire a GraphQL request."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post(
        "/graphql/",
        data=payload,
        content_type="application/json",
    )
