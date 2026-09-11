from django.urls import path

from .category_views import CategoryListCreateView

urlpatterns = [
    path('', CategoryListCreateView.as_view(), name='category-list-create'),
]
