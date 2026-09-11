from rest_framework import generics

from .models import Category
from .permissions import IsNormalUserOrReadOnly
from .serializers import CategorySerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
    permission_classes = [IsNormalUserOrReadOnly]
