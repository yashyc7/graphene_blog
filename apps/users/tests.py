"""
Tests for users app — Author queries and mutations
"""

import pytest

from apps.users.models import Author
from conftest import gql

# ── Queries ──────────────────────────────────────────────────────────────────

ALL_AUTHORS = """
    query {
        allAuthors {
            id
            name
            email
            bio
        }
    }
"""

AUTHOR_BY_ID = """
    query GetAuthor($id: ID!) {
        authorById(id: $id) {
            id
            name
            email
        }
    }
"""

# ── Mutations ─────────────────────────────────────────────────────────────────

CREATE_AUTHOR = """
    mutation CreateAuthor($input: CreateAuthorInput!) {
        createAuthor(input: $input) {
            author { id name email bio }
            errors { field message }
        }
    }
"""

UPDATE_AUTHOR = """
    mutation UpdateAuthor($id: ID!, $input: UpdateAuthorInput!) {
        updateAuthor(id: $id, input: $input) {
            author { id name email bio }
            errors { field message }
        }
    }
"""

DELETE_AUTHOR = """
    mutation DeleteAuthor($id: ID!) {
        deleteAuthor(id: $id) {
            success
            errors { field message }
        }
    }
"""


# ── Query Tests ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAuthorQueries:

    def test_all_authors_empty(self, client):
        res = gql(client, ALL_AUTHORS)
        assert res.status_code == 200
        assert res.json()["data"]["allAuthors"] == []

    def test_all_authors_returns_list(self, client, author):
        res = gql(client, ALL_AUTHORS)
        data = res.json()["data"]["allAuthors"]
        assert len(data) == 1
        assert data[0]["name"] == "Yash"
        assert data[0]["email"] == "yash@example.com"

    def test_all_authors_multiple(self, client, author, second_author):
        res = gql(client, ALL_AUTHORS)
        data = res.json()["data"]["allAuthors"]
        assert len(data) == 2

    def test_author_by_id_found(self, client, author):
        res = gql(client, AUTHOR_BY_ID, {"id": str(author.id)})
        data = res.json()["data"]["authorById"]
        assert data["name"] == "Yash"
        assert data["email"] == "yash@example.com"

    def test_author_by_id_not_found_returns_null(self, client):
        res = gql(client, AUTHOR_BY_ID, {"id": "9999"})
        assert res.json()["data"]["authorById"] is None


# ── Mutation Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCreateAuthor:

    def test_create_author_success(self, client):
        res = gql(
            client,
            CREATE_AUTHOR,
            {"input": {"name": "Bob", "email": "bob@example.com", "bio": "Dev"}},
        )
        data = res.json()["data"]["createAuthor"]
        assert data["errors"] == []
        assert data["author"]["name"] == "Bob"
        assert data["author"]["email"] == "bob@example.com"
        assert Author.objects.filter(email="bob@example.com").exists()

    def test_create_author_without_bio(self, client):
        res = gql(
            client,
            CREATE_AUTHOR,
            {"input": {"name": "Bob", "email": "bob@example.com"}},
        )
        data = res.json()["data"]["createAuthor"]
        assert data["errors"] == []
        assert data["author"]["bio"] == ""

    def test_create_author_invalid_email(self, client):
        res = gql(
            client, CREATE_AUTHOR, {"input": {"name": "Bob", "email": "not-an-email"}}
        )
        data = res.json()["data"]["createAuthor"]
        assert data["author"] is None
        assert any(e["field"] == "email" for e in data["errors"])

    def test_create_author_blank_name(self, client):
        res = gql(
            client, CREATE_AUTHOR, {"input": {"name": "  ", "email": "bob@example.com"}}
        )
        data = res.json()["data"]["createAuthor"]
        assert data["author"] is None
        assert any(e["field"] == "name" for e in data["errors"])

    def test_create_author_duplicate_email(self, client, author):
        res = gql(
            client,
            CREATE_AUTHOR,
            {"input": {"name": "Dup", "email": "yash@example.com"}},
        )
        data = res.json()["data"]["createAuthor"]
        assert data["author"] is None
        assert len(data["errors"]) > 0


@pytest.mark.django_db
class TestUpdateAuthor:

    def test_update_author_name(self, client, author):
        res = gql(
            client,
            UPDATE_AUTHOR,
            {"id": str(author.id), "input": {"name": "Yash Updated"}},
        )
        data = res.json()["data"]["updateAuthor"]
        assert data["errors"] == []
        assert data["author"]["name"] == "Yash Updated"

    def test_update_author_email(self, client, author):
        res = gql(
            client,
            UPDATE_AUTHOR,
            {"id": str(author.id), "input": {"email": "new@example.com"}},
        )
        data = res.json()["data"]["updateAuthor"]
        assert data["errors"] == []
        assert data["author"]["email"] == "new@example.com"

    def test_update_author_not_found(self, client):
        res = gql(client, UPDATE_AUTHOR, {"id": "9999", "input": {"name": "Ghost"}})
        data = res.json()["data"]["updateAuthor"]
        assert data["author"] is None
        assert any(e["field"] == "id" for e in data["errors"])

    def test_update_author_invalid_email(self, client, author):
        res = gql(
            client,
            UPDATE_AUTHOR,
            {"id": str(author.id), "input": {"email": "bad-email"}},
        )
        data = res.json()["data"]["updateAuthor"]
        assert data["author"] is None
        assert any(e["field"] == "email" for e in data["errors"])


@pytest.mark.django_db
class TestDeleteAuthor:

    def test_delete_author_success(self, client, author):
        res = gql(client, DELETE_AUTHOR, {"id": str(author.id)})
        data = res.json()["data"]["deleteAuthor"]
        assert data["success"] is True
        assert data["errors"] == []
        assert not Author.objects.filter(id=author.id).exists()

    def test_delete_author_not_found(self, client):
        res = gql(client, DELETE_AUTHOR, {"id": "9999"})
        data = res.json()["data"]["deleteAuthor"]
        assert data["success"] is False
        assert len(data["errors"]) > 0
