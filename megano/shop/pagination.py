from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# class CatalogPagination(PageNumberPagination):
#     page_size = 5
#     page_size_query_param = page_size
#     max_page_size = 30
#
#     def get_paginated_response(self, data):
#         last_page_number = self.page.paginator.count
#         return Response({
#             'items': data,
#             'currentPage': self.page.number,
#             'lastPage': last_page_number
#         })

class CatalogPagination(PageNumberPagination):
    page_size = 2
    def get_paginated_response(self, data):
        print('current', self.page.number)
        print('last', self.page.paginator.count)
        return Response(OrderedDict([
             ('items', data),
             ('currentPage', self.page.number),
             ('lastPage', self.page.paginator.count)
         ]))