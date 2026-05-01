import graphene
from .models import Post
from .types import PostType


class PostQuery(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    published_posts = graphene.List(PostType)
    post_by_id= graphene.Field(PostType,id=graphene.ID(required=True))


    def resolve_all_posts(self,info):
        return Post.objects.select_related("author").all()
    
    def resolve_published_posts(self,info):
        return Post.objects.select_related("author").filter(status=Post.Status.PUBLISHED)
    
    def resolve_post_by_id(self,info,id:str):
        try:
            return Post.objects.select_related("author").get(pk=id)
        except Post.DoesNotExist:
            return None 