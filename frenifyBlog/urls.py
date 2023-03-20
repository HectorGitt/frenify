from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('twitter_login', views.twitter_login, name='twitter_login'),
    path('connect_twitter', views.connect_twitter, name='connect_twitter'),
    path('twitter_logout', views.twitter_logout, name='logout'),
    path('callback', views.callback, name='callback'),
    path('blog/<slug:slug>', views.BlogDetailView.as_view(), name='blog_post'),
    path('blog/<slug:slug>/like', views.blog_like, name='blog_like'),
]

#added media upload root directory to url paths
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

#added static files root directory to url paths
urlpatterns += staticfiles_urlpatterns()