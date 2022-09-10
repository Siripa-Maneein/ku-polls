"""The models module provides the core objects of polls app(Question and Choice)."""
import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """A Question class create questions with published date and end date."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ended', null=True)

    def __str__(self):
        """Showing the question text."""
        return self.question_text

    def was_published_recently(self):
        """Check if the question was published recently (within 1 day)"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """A Choice class creates choices for Question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Showing the choice text."""
        return self.choice_text
