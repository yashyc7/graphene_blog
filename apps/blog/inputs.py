import graphene


class CreatePostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    author_id = graphene.ID(required=True)
    status = graphene.String(default_value="draft")


class UpdatePostInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String()
    status = graphene.String()
