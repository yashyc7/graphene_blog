import graphene
from apps.users.schema import AuthorQuery
from apps.blog.schema import PostQuery

# Multiple inheritence- merges all query into one root schema

class Query(AuthorQuery,PostQuery,graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)