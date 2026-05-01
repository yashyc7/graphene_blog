"""
shared types.py at the root level which can be used by all apps for error handeling and other stuffs
"""

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
