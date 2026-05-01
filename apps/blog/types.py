from graphene_django import DjangoObjectType

from .models import Post


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "status",
            "created_at",
            "updated_at",
        )
