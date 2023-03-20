from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .authorization import create_update_user_from_twitter
from django.views.generic.list import ListView
import datetime
from twitter_api.twitter_api import TwitterAPI
from django.views.generic import DetailView

from .models import BlogPost, TwitterUser, TwitterAuthToken

# Create your views here.



def home(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'frenifyBlog/index.html', {'blog_posts': blog_posts})

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'frenifyBlog/blog_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_post'] = self.object
        if self.request.user.is_authenticated and self.object.liked_by.filter(user=self.request.user).first():
            context['is_liked'] = True
        else:
            context['is_liked'] = False
        return context

@login_required
@never_cache
def blog_like(request, slug):
    blog_post = get_object_or_404(BlogPost, slug=slug)
    twitter_user = TwitterUser.objects.filter(user=request.user).first()
    if blog_post.liked_by.filter().first():
        blog_post.liked_by.remove(twitter_user)
    else:
        blog_post.liked_by.add(twitter_user)
    blog_post.save()
    
    return redirect('blog_post', slug=slug)


















def login_user(request):
    """_handle login request_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _renders page with next variable for redirect_
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    else:
        request.session['next'] = request.GET.get('next', '/')
        return render(request, 'frenifyBlog/login.html', {'next': next})
    
@never_cache
def twitter_login(request):
    """_Handles twitter oauth login_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_redirect_: _redirect to twitter authorization url_
    """
    twitter_api = TwitterAPI()
    #get tokens and authorization url
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.add_message(request, messages.ERROR, 'Unable to login. Please try again.')
        return render(request, 'authorization/error_page.html')
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        #if user not found with the auth tokens
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            twitter_auth_token.save()
        else:
            #if found, change the auth token secret to updated secret key
            twitter_auth_token.oauth_token_secret = oauth_token_secret
            twitter_auth_token.save()
        return redirect(url) 
def callback(request):
    """_handle twitter api oauth login callback and display appropriate errors _

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _description_
    """
    #if twitter oauth login was denied
    if 'denied' in request.GET:
        messages.add_message(request, messages.ERROR, 'Unable to login or login canceled. Please try again.')
        return render(request, 'frenifyBlog/error_page.html')
    twitter_api = TwitterAPI()
    #get tokens from callback request object
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    #if auth token is found for twitter user
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        #if access
        if access_token is not None and access_token_secret is not None:
            #get twitter user object that match last auth token
            user = TwitterAuthToken.objects.filter(oauth_token=access_token).last()
            #save tokens if user is not found or if user token is needs to be updated
            if user is None or user.oauth_token_secret != access_token_secret : 
                twitter_auth_token.oauth_token = access_token
                twitter_auth_token.oauth_token_secret = access_token_secret
                twitter_auth_token.save()
            else:
                twitter_auth_token.delete()
            # get user info from twitter api
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                
                date = info[0]['created_at']
                account_month = (datetime.date.today().year - date.date().year) * 12 + (datetime.date.today().month - date.date().month)
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'], name=info[0]['name'], profile_image_url=info[0]['profile_image_url'], account_months=account_month)
                #check if user token not none
                if user is not None:
                    twitter_user_new.twitter_oauth_token = user
                else:
                    twitter_user_new.twitter_oauth_token = twitter_auth_token
                #create new user in database
                user, twitter_user = create_update_user_from_twitter(twitter_user_new)
                #if user successfully created
                if user is not None:
                    #login
                    login(request, user)
                    #try to return to initial page from next url
                    try:
                        return redirect(request.session['next'])
                    except:
                        return redirect('home')
                    
            else:
                #if get me twitter api returns none
                messages.add_message(request, messages.ERROR, 'Unable to get profile details. Please try again.')
                return render(request, 'frenifyBlog/error_page.html')
        else:
            #if access token not returned from twitter api
            messages.add_message(request, messages.ERROR, 'Unable to get access token. Please try again.')
            return render(request, 'frenifyBlog/error_page.html')
    else:
        #if access token is not found in the database
        messages.add_message(request, messages.ERROR, 'Unable to retrieve access token. Please try again.')
        return render(request, 'frenifyBlog/error_page.html')

@login_required
def twitter_logout(request):
    """_handles twitter oauth logout_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _redirect to homepage_
    """
    logout(request)
    return redirect('home')

def connect_twitter(request):
    """_Redirects to twitter oauth login view_

    Args:
        request (_request_object_): _description_

    Returns:
        _http_response_: _redirect to twitter oauth login view_
    """
    #get next url from request and save to session(later used by twitter_login view)
    request.session['next'] = request.GET.get('next', '/')
    return redirect('twitter_login')
    
