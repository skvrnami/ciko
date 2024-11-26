from django.db import models

class Text(models.Model):
    id = models.IntegerField("id", primary_key=True)
    link = models.CharField(max_length=200, unique=True)
    publication_date = models.DateTimeField("date published")
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    source = models.CharField(max_length=100, default="")
    read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Highlight(models.Model):
    text = models.ForeignKey('Text', on_delete=models.CASCADE, related_name='highlights')
    content = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Highlight from {self.text.title}"