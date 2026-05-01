import graphene


class ErrorType(graphene.ObjectType):
    field = graphene.String()
    message = graphene.String()

    @staticmethod
    def from_dict(field: str, message: str) -> "ErrorType":
        err = ErrorType()
        err.field = field
        err.message = message
        return err
