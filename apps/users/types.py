""" 
ObjectType = GraphQL's way of saying "this is what a Post/Author looks like to the client
"""

import graphene
from graphene_django import DjangoObjectType
from .models import Author

class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = ("id","name","email","bio","created_at")

        # we explicitly define fields which means = 
        # secure , no accidental fields leaks 