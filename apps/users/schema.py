import graphene

from .models import Author
from .types import AuthorType


class AuthorQuery(graphene.ObjectType):
    all_authors = graphene.List(AuthorType)
    author_by_id = graphene.Field(AuthorType, id=graphene.ID(required=True))

    def resolve_all_authors(self, info):
        return Author.objects.all()

    def resolve_author_by_id(self, info, id):
        try:
            return Author.objects.get(id=id)
        except Author.DoesNotExist:
            return None
