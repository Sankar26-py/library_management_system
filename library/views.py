from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets,status
from .models import Book
from .serializers import BookSerializer
from rest_framework.response import Response
from .tasks import send_book_notification
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator


def book_list(request):
    books = Book.objects.all()
    return render(request,'book_list.html',{'books':books})

def add_book(request):
    if request.method=='POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        send_book_notification.delay(title)
        Book.objects.create(title=title,author=author)       
        return redirect('book_list')
    return render(request,'add_book.html')

# Create your views here.
class BookViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self,request):
        books = Book.objects.all()
        search = request.GET.get('search')
        if search:
            books = books.filter(title__icontains = search) | books.filter(author__icontains =search)
        paginator = Paginator(books, 5)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        serializer_data = BookSerializer(page_obj,many=True)
        #return Response(serializer_data.data,status=status.HTTP_200_OK)
        return Response({"count": paginator.count,"page": page_obj.number,"results": serializer_data.data},status=status.HTTP_200_OK)
    
    def retrieve(self,request,pk):
        book = Book.objects.get(id=pk)
        if not book:
            return Response(f"Book with id {pk} not found",status=status.HTTP_404_NOT_FOUND)
        serializer_data = BookSerializer(book)
        return Response(serializer_data.data,status=status.HTTP_200_OK)
    
    def create(self,request):
        if not request.user.is_staff:
            return Response("Only admin can create book",status=status.HTTP_403_FORBIDDEN)
        
        serializer = BookSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def update(self,request,pk):
        book = Book.objects.get(id=pk)
        serializer =BookSerializer(book,data=request.data)
        if serializer.is_valid():
            serializer.save()
            book = Book.objects.get(id=pk)
            serializer =BookSerializer(book)
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self,request,pk):
        book = Book.objects.get(id=pk)
        serializer =BookSerializer(book,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            book = Book.objects.get(id=pk)
            serializer =BookSerializer(book)
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self,request,pk):
        if not request.user.is_staff:
            return Response("Only admin can create book",status=status.HTTP_403_FORBIDDEN)
        queryset = Book.objects.get(id=pk)
        queryset.delete()
        return Response(f"Book deleted")
    
    def issue(self,requet,pk):
        book = get_object_or_404(Book, id=pk)

        if not book.is_available:
            return Response({"error": "Already issued"}, status=status.HTTP_400_BAD_REQUEST)
        
        book.is_available = False
        book.save()

        send_book_notification.delay(book.title)

        return Response({"message": f"Book '{book.title}' issued successfully"}, status=status.HTTP_200_OK)
    
    def return_book(self,request,pk):

        book = get_object_or_404(Book,id=pk)

        if book.is_available:
            return Response({"error":"Book is not issued"},status=status.HTTP_400_BAD_REQUEST)
        
        book.is_available = True
        book.save()

        return Response({"message":f"Book '{book.title}' returned successfully"},status=status.HTTP_200_OK)