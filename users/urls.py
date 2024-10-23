from django.urls import path
from .views import LoginView, UserListView, UserDetailView, RecipientListView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('recipients/', RecipientListView.as_view(), name='recipients-list'),
]
