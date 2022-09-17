"""The models module provides the core objects of polls app(Question and Choice)."""
import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """A Question class create questions with published date and end date."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ended', null=True)

    def __str__(self):
        """Show the question text."""
        return self.question_text

    def was_published_recently(self):
        """Check if the question was published recently (within 1 day)."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return True if the current time is more than published date."""
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """
        Check if visitor can vote this question.

        Visitors can vote only if the question is published,
        and the current time is still less than or equal to the ending date or
        no ending date is set.
        """
        return self.is_published() and ((self.end_date is None)
                                        or (timezone.now() <= self.end_date))

    def get_voted_choice(self, user):
        """Get the choice that is already voted."""
        for choice in self.choice_set.all():
            if Vote.objects.filter(choice=choice, user=user).exists():
                return choice
        return None


class Choice(models.Model):
    """A Choice class creates choices for Question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Show the choice text."""
        return self.choice_text

    @property
    def vote(self):
        """Count the number of votes for this choice."""
        return Vote.objects.filter(choice=self).count()


class Vote(models.Model):
    """A vote by a user for a question."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    @property
    def question(self):
        return self.choice.question

