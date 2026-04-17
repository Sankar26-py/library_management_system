from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from library.views import BookViewSet,add_book,book_list

# API VIEWSET MAPPING

book_list_api = BookViewSet.as_view({
    'get':'list',
    'post':'create'
})

book_detail_api = BookViewSet.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'partial_update',
    'delete':'destroy'
})

book_issue = BookViewSet.as_view({
    'put':'issue'
})

book_return = BookViewSet.as_view({
    'put' : 'return_book'
})

# URL PATTERNS

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('',book_list,name='book_list'),
    path('add/',add_book,name='add_book'),

    path('api/books/',book_list_api,name = 'book_list_api'),
    path('api/books/<int:pk>/',book_detail_api,name = 'book_detail_api'),
    path('api/books/<int:pk>/issue/',book_issue,name = 'book_issue'),
    path('api/books/<int:pk>/return/',book_return,name = 'book_return'),

]