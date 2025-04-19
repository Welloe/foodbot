from django.db import models

class ChatResponse(models.Model):
    role = models.CharField(max_length=1)  # 'A' or 'B'
    message = models.TextField()
    is_vegetarian_or_vegan = models.BooleanField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.message[:30]}..."