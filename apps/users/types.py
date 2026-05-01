from graphene_django import DjangoObjectType

from .models import Author


class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = ("id", "name", "email", "bio", "created_at")

        # we explicitly define fields which means =
        # secure , no accidental fields leaks
