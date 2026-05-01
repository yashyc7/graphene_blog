import graphene


class CreateAuthorInput(graphene.InputObjectType):
    """Input shape for creating an author — validated before hitting the DB."""

    name = graphene.String(required=True)
    email = graphene.String(required=True)
    bio = graphene.String(default_value=" ")


class UpdateAuthorInput(graphene.InputObjectType):
    """All fields optional - only update whats provided"""

    name = graphene.String()
    email = graphene.String()
    bio = graphene.String()
