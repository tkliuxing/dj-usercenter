import django_filters
from . import models


class UserFullNameFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='contains', label='姓名')

    class Meta:
        model = models.User
        fields = [
            'full_name'
        ]
