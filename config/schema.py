import graphene

from apps.blog.mutations import PostMutation
from apps.blog.schema import PostQuery
from apps.users.mutations import AuthorMutation
from apps.users.schema import AuthorQuery


class Query(AuthorQuery, PostQuery, graphene.ObjectType):
    pass


# Same composition pattern as Query — each app owns its Mutation class
class Mutation(AuthorMutation, PostMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
