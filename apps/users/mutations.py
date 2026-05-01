import graphene
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError

from apps.common.error_types import ErrorType

from .inputs import CreateAuthorInput, UpdateAuthorInput
from .models import Author
from .types import AuthorType


class CreateAuthor(graphene.Mutation):
    class Arguments:
        input = CreateAuthorInput(required=True)

    # Payload — always return both fields
    author = graphene.Field(AuthorType)
    errors = graphene.List(graphene.NonNull(ErrorType))

    def mutate(self, info, input: CreateAuthorInput):
        errors = []

        # --- Validation layer ---
        name = input.name.strip()
        email = input.email.strip().lower()

        if not name:
            errors.append(ErrorType.from_dict("name", "Name cannot be blank."))

        try:
            validate_email(email)
        except ValidationError:
            errors.append(
                ErrorType.from_dict("email", "Provide a valid email address.")
            )

        if errors:
            return CreateAuthor(author=None, errors=errors)

        # --- Business logic layer ---
        try:
            author = Author.objects.create(
                name=name, email=email, bio=input.bio.strip()
            )
            return CreateAuthor(author=author, errors=[])
        except IntegrityError:
            return CreateAuthor(
                author=None,
                errors=[
                    ErrorType.from_dict(
                        "email", "An author with this email already exists."
                    )
                ],
            )


class UpdateAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UpdateAuthorInput(required=True)

    author = graphene.Field(AuthorType)
    errors = graphene.List(graphene.NonNull(ErrorType))

    def mutate(self, info, id: str, input: UpdateAuthorInput):
        try:
            author = Author.objects.get(pk=id)
        except Author.DoesNotExist:
            return UpdateAuthor(
                author=None,
                errors=[ErrorType.from_dict("id", f"Author with id={id} not found.")],
            )

        errors = []

        # Only validate + apply fields that were actually provided
        if input.name is not None:
            name = input.name.strip()
            if not name:
                errors.append(ErrorType.from_dict("name", "Name cannot be blank."))
            else:
                author.name = name

        if input.email is not None:
            email = input.email.strip().lower()
            try:
                validate_email(email)
                author.email = email
            except ValidationError:
                errors.append(
                    ErrorType.from_dict("email", "Provide a valid email address.")
                )

        if input.bio is not None:
            author.bio = input.bio.strip()

        if errors:
            return UpdateAuthor(author=None, errors=errors)

        try:
            author.save()
            return UpdateAuthor(author=author, errors=[])
        except IntegrityError:
            return UpdateAuthor(
                author=None,
                errors=[
                    ErrorType.from_dict(
                        "email", "Email already taken by another author."
                    )
                ],
            )


class DeleteAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.NonNull(ErrorType))

    def mutate(self, info, id: str):
        try:
            author = Author.objects.get(pk=id)
            author.delete()
            return DeleteAuthor(success=True, errors=[])
        except Author.DoesNotExist:
            return DeleteAuthor(
                success=False,
                errors=[ErrorType.from_dict("id", f"Author with id={id} not found.")],
            )


class AuthorMutation(graphene.ObjectType):
    create_author = CreateAuthor.Field()
    update_author = UpdateAuthor.Field()
    delete_author = DeleteAuthor.Field()
