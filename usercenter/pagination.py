from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class UCPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_query_param = 'page'
    page_size = None

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.page.has_next()),
            ('previous', self.page.has_previous()),
            ('data', data)
        ]))
