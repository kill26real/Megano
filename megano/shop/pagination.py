from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CatalogPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = page_size
    max_page_size = 30

    def get_paginated_response(self, data):
        last_page_number = self.page.paginator.count
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': last_page_number
        })

class CatalogsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = page_size
    max_page_size = 30
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })