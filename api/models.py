# api/models.py

from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    image = models.ImageField(upload_to='faculty_images/')
    face_encoding = models.BinaryField()  # Store face encoding as binary data.

    def __str__(self):
        return self.name
