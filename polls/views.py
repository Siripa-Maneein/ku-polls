"""Contains views of the polls application."""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from .models import Question, Choice, Vote


def get_voted_choice(question, user):
    try:
        return Vote.objects.get(choice__question=question, user=user).choice
    except Vote.DoesNotExist:
        return None


class BaseIndexView(generic.DetailView):
    """A class representing a view for base url."""

    def get(self, request, *args, **kwargs):
        """When the base url is called, it will be redirect to polls index."""
        return HttpResponseRedirect(reverse('polls:index'))


class IndexView(generic.ListView):
    """A class representing an index view."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions.

        Those set to be published in the future will not be included.
        """
        published_id_list = [q.id for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(
            id__in=published_id_list
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """A class for detail view of a poll."""
    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, *args, **kwargs):
        try:
            question = Question.objects.get(pk=self.kwargs['pk'])
            if not question.can_vote():
                messages.error(request, "‼️ Voting is not allowed for this question.")
                return HttpResponseRedirect(reverse('polls:index'))
            if request.user.is_authenticated:
                return render(request, 'polls/detail.html', {
                    'question': question,
                    'voted_choice': get_voted_choice(question, request.user)
                })
            else:
                return render(request, 'polls/detail.html', {
                    'question': question,
                })
        except Question.DoesNotExist:
            messages.error(request, "‼️ The question you're looking for does not exist.")
            return HttpResponseRedirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    """A class representing a result view."""

    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        published_id_list = [q.id for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(id__in=published_id_list)


@login_required
def vote(request, question_id):
    """Return correct response to vote view request."""
    user = request.user
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        if not KeyError:
            messages.error(request, "‼️ You didn't select a choice.")
        return render(request, 'polls/detail.html', {
            'question': question,
            'voted_choice': get_voted_choice(question, user)
        })
    else:
        # user already vote this choice
        if Vote.objects.filter(choice=selected_choice, user=user).exists():
            messages.error(request, "‼️ You have already voted this choice.")
            return render(request, 'polls/detail.html', {
                'question': question,
                'voted_choice': get_voted_choice(question, user)
            })
        # user change choice from the same question
        elif Vote.objects.filter(user=user, choice__question=question).exists():
            old_choice = get_voted_choice(question, user)
            old_choice.vote_set.filter(user=user).delete()
            old_choice.save()
            messages.success(request, f"✅ Your choice was successfully changed from "
                                      f"'{old_choice.choice_text}' "
                                      f"to '{selected_choice.choice_text}'.")
        # the question has never been voted by the user before
        else:
            messages.success(request, "✅ Your choice was successfully recorded. Thank you.")
        # create new vote and update number of votes for selected choice
        Vote.objects.create(user=user, choice=selected_choice)
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
