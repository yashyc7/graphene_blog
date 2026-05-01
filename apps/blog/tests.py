"""
Tests for blog app — Post queries and mutations
"""

import pytest

from apps.blog.models import Post
from conftest import gql

# ── Queries ───────────────────────────────────────────────────────────────────

ALL_POSTS = """
    query {
        allPosts {
            id
            title
            status
            author { name }
        }
    }
"""

PUBLISHED_POSTS = """
    query {
        publishedPosts {
            id
            title
            status
            author { name }
        }
    }
"""

POST_BY_ID = """
    query GetPost($id: ID!) {
        postById(id: $id) {
            id
            title
            content
            status
            author { name }
        }
    }
"""

# ── Mutations ─────────────────────────────────────────────────────────────────

CREATE_POST = """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            post { id title content status author { name } }
            errors { field message }
        }
    }
"""

UPDATE_POST = """
    mutation UpdatePost($id: ID!, $input: UpdatePostInput!) {
        updatePost(id: $id, input: $input) {
            post { id title status }
            errors { field message }
        }
    }
"""

DELETE_POST = """
    mutation DeletePost($id: ID!) {
        deletePost(id: $id) {
            success
            errors { field message }
        }
    }
"""


# ── Query Tests ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPostQueries:

    def test_all_posts_empty(self, client):
        res = gql(client, ALL_POSTS)
        assert res.json()["data"]["allPosts"] == []

    def test_all_posts_returns_both_statuses(self, client, published_post, draft_post):
        res = gql(client, ALL_POSTS)
        data = res.json()["data"]["allPosts"]
        assert len(data) == 2
        titles = [p["title"] for p in data]
        assert "Published Post" in titles
        assert "Draft Post" in titles

    def test_published_posts_only_returns_published(
        self, client, published_post, draft_post
    ):
        res = gql(client, PUBLISHED_POSTS)
        data = res.json()["data"]["publishedPosts"]
        assert all(p["status"] == "PUBLISHED" for p in data)  # ← uppercase
        titles = [p["title"] for p in data]
        assert "Published Post" in titles
        assert "Draft Post" not in titles

    def test_published_posts_empty_when_none_published(self, client, draft_post):
        res = gql(client, PUBLISHED_POSTS)
        assert res.json()["data"]["publishedPosts"] == []

    def test_post_by_id_found(self, client, published_post):
        res = gql(client, POST_BY_ID, {"id": str(published_post.id)})
        data = res.json()["data"]["postById"]
        assert data["title"] == "Published Post"
        assert data["author"]["name"] == "Yash"

    def test_post_by_id_not_found_returns_null(self, client):
        res = gql(client, POST_BY_ID, {"id": "9999"})
        assert res.json()["data"]["postById"] is None

    def test_post_includes_author(self, client, published_post):
        res = gql(client, POST_BY_ID, {"id": str(published_post.id)})
        data = res.json()["data"]["postById"]
        assert data["author"]["name"] == "Yash"


# ── Mutation Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCreatePost:

    def test_create_post_success(self, client, author):
        res = gql(
            client,
            CREATE_POST,
            {
                "input": {
                    "title": "New Post",
                    "content": "Content here.",
                    "authorId": str(author.id),
                    "status": "published",
                }
            },
        )
        data = res.json()["data"]["createPost"]
        assert data["errors"] == []
        assert data["post"]["title"] == "New Post"
        assert data["post"]["status"] == "PUBLISHED"
        assert Post.objects.filter(title="New Post").exists()

    def test_create_post_default_status_is_draft(self, client, author):
        res = gql(
            client,
            CREATE_POST,
            {
                "input": {
                    "title": "Draft Post",
                    "content": "Content.",
                    "authorId": str(author.id),
                }
            },
        )
        data = res.json()["data"]["createPost"]
        assert data["errors"] == []
        assert data["post"]["status"] == "DRAFT"

    def test_create_post_blank_title(self, client, author):
        res = gql(
            client,
            CREATE_POST,
            {
                "input": {
                    "title": "  ",
                    "content": "Content.",
                    "authorId": str(author.id),
                }
            },
        )
        data = res.json()["data"]["createPost"]
        assert data["post"] is None
        assert any(e["field"] == "title" for e in data["errors"])

    def test_create_post_invalid_status(self, client, author):
        res = gql(
            client,
            CREATE_POST,
            {
                "input": {
                    "title": "Post",
                    "content": "Content.",
                    "authorId": str(author.id),
                    "status": "invalid_status",
                }
            },
        )
        data = res.json()["data"]["createPost"]
        assert data["post"] is None
        assert any(e["field"] == "status" for e in data["errors"])

    def test_create_post_author_not_found(self, client):
        res = gql(
            client,
            CREATE_POST,
            {
                "input": {
                    "title": "Post",
                    "content": "Content.",
                    "authorId": "9999",
                }
            },
        )
        data = res.json()["data"]["createPost"]
        assert data["post"] is None
        assert any(e["field"] == "author_id" for e in data["errors"])

    def test_create_post_blank_content(self, client, author):
        res = gql(
            client,
            CREATE_POST,
            {
                "input": {
                    "title": "Post",
                    "content": "  ",
                    "authorId": str(author.id),
                }
            },
        )
        data = res.json()["data"]["createPost"]
        assert data["post"] is None
        assert any(e["field"] == "content" for e in data["errors"])


@pytest.mark.django_db
class TestUpdatePost:

    def test_update_post_title(self, client, published_post):
        res = gql(
            client,
            UPDATE_POST,
            {"id": str(published_post.id), "input": {"title": "Updated Title"}},
        )
        data = res.json()["data"]["updatePost"]
        assert data["errors"] == []
        assert data["post"]["title"] == "Updated Title"

    def test_update_post_status_to_draft(self, client, published_post):
        res = gql(
            client,
            UPDATE_POST,
            {"id": str(published_post.id), "input": {"status": "draft"}},
        )
        data = res.json()["data"]["updatePost"]
        assert data["errors"] == []
        assert data["post"]["status"] == "DRAFT"

    def test_update_post_invalid_status(self, client, published_post):
        res = gql(
            client,
            UPDATE_POST,
            {"id": str(published_post.id), "input": {"status": "garbage"}},
        )
        data = res.json()["data"]["updatePost"]
        assert data["post"] is None
        assert any(e["field"] == "status" for e in data["errors"])

    def test_update_post_not_found(self, client):
        res = gql(client, UPDATE_POST, {"id": "9999", "input": {"title": "Ghost"}})
        data = res.json()["data"]["updatePost"]
        assert data["post"] is None
        assert any(e["field"] == "id" for e in data["errors"])

    def test_update_post_blank_title(self, client, published_post):
        res = gql(
            client,
            UPDATE_POST,
            {"id": str(published_post.id), "input": {"title": "  "}},
        )
        data = res.json()["data"]["updatePost"]
        assert data["post"] is None
        assert any(e["field"] == "title" for e in data["errors"])


@pytest.mark.django_db
class TestDeletePost:

    def test_delete_post_success(self, client, published_post):
        res = gql(client, DELETE_POST, {"id": str(published_post.id)})
        data = res.json()["data"]["deletePost"]
        assert data["success"] is True
        assert data["errors"] == []
        assert not Post.objects.filter(id=published_post.id).exists()

    def test_delete_post_not_found(self, client):
        res = gql(client, DELETE_POST, {"id": "9999"})
        data = res.json()["data"]["deletePost"]
        assert data["success"] is False
        assert len(data["errors"]) > 0
