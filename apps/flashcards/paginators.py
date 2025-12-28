from rest_framework.pagination import PageNumberPagination


class DeckListPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 25
    

class ReviewListPagination(PageNumberPagination):

    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 25

    
class CardListPagination(PageNumberPagination):

    page_size=5
    page_size_query_param = 'page_size'
    max_page_size = 25

