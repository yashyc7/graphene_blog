from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["email"])]

    def __str__(self) -> str:
        return self.name
