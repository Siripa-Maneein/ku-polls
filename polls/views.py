from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, path
from django.views import generic
from django.contrib import messages
from django.http import Http404
from django.views.generic import RedirectView


from .models import Question, Choice


class BaseIndexView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        """When the base url is called, it will be redirect to polls index."""
        return HttpResponseRedirect(reverse('polls:index'))


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        published_id_list = [q.id for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(
            id__in=published_id_list
        ).order_by('-pub_date')[:5]


def detail(request, pk):
    try:
        question = Question.objects.get(pk=pk)
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this question.")
            return HttpResponseRedirect(reverse('polls:index'))
        return render(request, 'polls/detail.html', {
            'question': question
        })
    except Question.DoesNotExist:
        messages.error(request, "The question you're looking for does not existed.")
        return HttpResponseRedirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_id_list = [q.id for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(id__in=published_id_list)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice,",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        messages.success(request, "Your choice successfully recorded. Thank you.")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
