from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/<slug:slug>', views.BlogDetailView.as_view(), name='blog_post'),
]

#added media upload root directory to url paths
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

#added static files root directory to url paths
urlpatterns += staticfiles_urlpatterns()