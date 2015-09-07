from django.db import models
from django.utils import timezone

class Deck(models.Model):
	author = models.ForeignKey('auth.User')
	title = models.CharField(max_length=200)
	cards = models.TextField()
	updated_at = models.DateTimeField(null=True)

	def publish(self):
		self.save()

	def __str__(self):
		return self.title

