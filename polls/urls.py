from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('polls/', views.IndexView.as_view(), name='index'),
    path('', views.BaseIndexView.as_view(), name='redirect-index'),
    path('polls/<int:pk>/', views.detail, name='detail'),
    path('polls/<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('polls/<int:question_id>/vote/', views.vote, name='vote'),
]

