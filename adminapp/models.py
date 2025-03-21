from django.db import models

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    categories = models.CharField(max_length=255) 
    description = models.TextField()
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True)


    def __str__(self):
        return self.name
    


class Conversation(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"User: {self.user_message[:50]}..."