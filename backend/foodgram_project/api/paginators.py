from rest_framework.pagination import PageNumberPagination


class PageNumberCustomPaginator(PageNumberPagination):
    '''
    Класс PageNumberCustomPaginator.
    '''
    page_size_query_param = 'limit'
