from django.shortcuts import render
from django.views.generic import DetailView

from .models import BlogPost

# Create your views here.



def home(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'frenifyBlog/index.html', {'blog_posts': blog_posts})

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'frenifyBlog/blog_post.html'