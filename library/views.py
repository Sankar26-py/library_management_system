from django.shortcuts import redirect, render
from rest_framework import viewsets,status
from .models import Book
from .serializers import BookSerializer
from rest_framework.response import Response


def book_list(request):
    books = Book.objects.all()
    return render(request,'book_list.html',{'books':books})

def add_book(request):
    if request.method=='POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        Book.objects.create(title=title,author=author)
        return redirect('book_list')
    return render(request,'add_book.html')

# Create your views here.
class BookViewSet(viewsets.ViewSet):

    def list(self,request):
        books = Book.objects.all()
        serializer_data = BookSerializer(books,many=True)
        return Response(serializer_data.data,status=status.HTTP_200_OK)
    
    def retrieve(self,request,pk):
        book = Book.objects.get(id=pk)
        serializer_data = BookSerializer(book)
        return Response(serializer_data.data,status=status.HTTP_200_OK)
    
    def create(self,request):
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
        queryset = Book.objects.get(id=pk)
        queryset.delete()
        return Response(f"Book deleted")

