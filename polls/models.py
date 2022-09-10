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

    def is_published(self):
        """Return True if the current time is more than published date."""
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """Visitors can vote only if the question is published,
        and the current time is still less than or equal to the ending date or
        no ending date is set."""
        return self.is_published() and ((self.end_date is None) or (timezone.now() <= self.end_date))


class Choice(models.Model):
    """A Choice class creates choices for Question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Showing the choice text."""
        return self.choice_text
