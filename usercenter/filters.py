import django_filters

from baseconfig.models import BaseConfigItem
from . import models


class UserFilterSet(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=BaseConfigItem.objects.all(), help_text='分类'
    )

    class Meta:
        model = models.User
        fields = (
            'full_name',
            'department',
            'is_active',
            'category',
            'func_groups__name',
        )


class UserFullNameFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='contains', label='姓名')

    class Meta:
        model = models.User
        fields = [
            'full_name',
            'department'
        ]
