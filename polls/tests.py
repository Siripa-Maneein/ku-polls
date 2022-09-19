"""Unit tests for polls application."""
import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Choice


class QuestionModelTests(TestCase):
    """Test cases for methods in Question."""

    def setUp(self):
        """Set future and old question for repeatable uses."""
        future_time = timezone.now() + datetime.timedelta(days=30)
        self.future_question = Question(pub_date=future_time)

        old_time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        self.old_question = Question(pub_date=old_time)

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        self.assertIs(self.future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        self.assertIs(self.old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_can_vote_with_future_published_question(self):
        """
        can_vote() returns False for questions whose pub_date
        is in the future.
        """
        self.assertIs(self.future_question.can_vote(), False)

    def test_can_vote_on_exactly_pub_date(self):
        """
        can_vote() returns True for questions whose pub_date
        is same as the current time.
        """
        with patch.object(timezone, 'now', return_value=datetime.datetime(2022, 10, 10, 12, 20)):
            self.assertIs(Question(pub_date=timezone.now()).can_vote(), True)

    def test_can_vote_on_exactly_end_date(self):
        """can_vote() return True on the ending date."""
        with patch.object(timezone, 'now', return_value=datetime.datetime(2022, 10, 10, 12, 20)):
            published_time = timezone.now() - timezone.timedelta(days=2)
            self.assertIs(Question(pub_date=published_time,
                                   end_date=timezone.now()).can_vote()
                          , True)

    def test_can_vote_with_current_time_after_end_date(self):
        """can_vote() returns False if current time passing the end date."""
        published_time = timezone.now() - timezone.timedelta(days=2)
        end_time = timezone.now() - timezone.timedelta(days=1)
        self.assertIs(Question(pub_date=published_time, end_date=end_time).can_vote(), False)

    def test_can_vote_with_no_end_date(self):
        """Can vote question with null end date anytime after the published date."""
        published_time = timezone.now() - timezone.timedelta(days=2)
        question_with_no_end_date = Question(pub_date=published_time)
        self.assertEqual(question_with_no_end_date.end_date, None)
        self.assertIs(question_with_no_end_date.can_vote(), True)

    def test_is_published(self):
        """is_published() returns True when the question is published."""
        self.assertIs(self.future_question.is_published(), False)
        published_question = self.old_question
        self.assertIs(published_question.is_published(), True)


def create_question(question_text, days=0):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """Test cases for index view of the app."""
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    """Test cases for detail view of the app."""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 302 redirecting to index page.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('polls:index'))

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_not_existing_question(self):
        """
        The detail view of a question that does not exist
        returns a 302 redirecting to index page.
        """
        url = reverse('polls:detail', args=(100,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('polls:index'))

    def test_passing_end_date_question(self):
        """
        The detail view of a question that the end date has passed
        returns a 302 redirecting to index page.
        """
        pub_date = timezone.now() - datetime.timedelta(days=2)
        end_date = timezone.now() - datetime.timedelta(days=1)
        question = Question.objects.create(question_text="What's up",
                                           pub_date=pub_date,
                                           end_date=end_date)
        url = reverse('polls:detail', args=(question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('polls:index'))


class QuestionResultViewTests(TestCase):
    """Test cases for result view of the app."""

    def test_future_question(self):
        """
        The result view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The result view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class UserAuthTest(django.test.TestCase):
    """Test cases for authentication."""

    def setUp(self):
        # superclass setUp creates a Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = create_question("First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """a user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        response = self.client.get(logout_url)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse('login'))

    def test_login_view(self):
        """a user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse("polls:index"))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)
