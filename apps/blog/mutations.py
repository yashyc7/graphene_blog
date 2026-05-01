import graphene

from apps.common.types import ErrorType
from apps.users.models import Author

from .inputs import CreatePostInput, UpdatePostInput
from .models import Post
from .types import PostType

VALID_STATUSES = {Post.Status.DRAFT, Post.Status.PUBLISHED}


class CreatePost(graphene.Mutation):
    class Arguments:
        input = CreatePostInput(required=True)

    post = graphene.Field(PostType)
    errors = graphene.List(graphene.NonNull(ErrorType))

    def mutate(self, info, input: CreatePostInput):
        errors = []

        title = input.title.strip()
        content = input.content.strip()
        status = input.status.strip().lower()

        if not title:
            errors.append(ErrorType.from_dict("title", "Title cannot be blank."))

        if not content:
            errors.append(ErrorType.from_dict("content", "Content cannot be blank."))

        if status not in VALID_STATUSES:
            errors.append(
                ErrorType.from_dict(
                    "status",
                    f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}",
                )
            )

        # Validate FK exists before hitting DB
        try:
            author = Author.objects.get(pk=input.author_id)
        except Author.DoesNotExist:
            errors.append(
                ErrorType.from_dict(
                    "author_id", f"Author id={input.author_id} not found."
                )
            )
            author = None

        if errors:
            return CreatePost(post=None, errors=errors)

        post = Post.objects.create(
            title=title,
            content=content,
            author=author,
            status=status,
        )
        return CreatePost(post=post, errors=[])


class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UpdatePostInput(required=True)

    post = graphene.Field(PostType)
    errors = graphene.List(graphene.NonNull(ErrorType))

    def mutate(self, info, id: str, input: UpdatePostInput):
        try:
            post = Post.objects.select_related("author").get(pk=id)
        except Post.DoesNotExist:
            return UpdatePost(
                post=None,
                errors=[ErrorType.from_dict("id", f"Post with id={id} not found.")],
            )

        errors = []

        if input.title is not None:
            title = input.title.strip()
            if not title:
                errors.append(ErrorType.from_dict("title", "Title cannot be blank."))
            else:
                post.title = title

        if input.content is not None:
            content = input.content.strip()
            if not content:
                errors.append(
                    ErrorType.from_dict("content", "Content cannot be blank.")
                )
            else:
                post.content = content

        if input.status is not None:
            status = input.status.strip().lower()
            if status not in VALID_STATUSES:
                errors.append(
                    ErrorType.from_dict(
                        "status",
                        f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}",
                    )
                )
            else:
                post.status = status

        if errors:
            return UpdatePost(post=None, errors=errors)

        post.save()
        return UpdatePost(post=post, errors=[])


class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.NonNull(ErrorType))

    def mutate(self, info, id: str):
        try:
            post = Post.objects.get(pk=id)
            post.delete()
            return DeletePost(success=True, errors=[])
        except Post.DoesNotExist:
            return DeletePost(
                success=False,
                errors=[ErrorType.from_dict("id", f"Post with id={id} not found.")],
            )


class PostMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
