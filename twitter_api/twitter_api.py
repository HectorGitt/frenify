import tweepy
from decouple import config
import datetime
import re

'''Twitter Oauth login handler'''

class TwitterAPI:
    def __init__(self):
        # Twitter API config variables
        self.api_key = config('TWITTER_API_KEY')
        self.api_secret = config('TWITTER_API_SECRET')
        self.client_id = config('TWITTER_CLIENT_ID')
        self.client_secret = config('TWITTER_CLIENT_SECRET')
        self.oauth_callback_url = config('TWITTER_OAUTH_CALLBACK_URL')
        self.access_token = config('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = config('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = config('TWITTER_BEARER_TOKEN')

        
    def twitter_login(self):        
        """_summary_:
            Get authurization url for twitter login

        Returns:
            _str_: _redirect_url_
            _str_: _api_request_token_
            _str_: _api_request_token_secret_     
        """
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        url = oauth1_user_handler.get_authorization_url(signin_with_twitter=True)
        request_token = oauth1_user_handler.request_token["oauth_token"]
        request_secret = oauth1_user_handler.request_token["oauth_token_secret"]
        return url, request_token, request_secret

    def twitter_callback(self,oauth_verifier, oauth_token, oauth_token_secret):
        """_summary_:
        Get access tokens from twitter api

        Args:
            oauth_verifier (_str_): _Returned from twitter api for access_
            oauth_token (_str_): _Returned from twitter api for access_
            oauth_token_secret (_str_): _Returned from twitter api for access_

        Returns:
            _str_: _access_token_
            _str_: _access_token_secret_
        """
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        oauth1_user_handler.request_token = {
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        }
        access_token, access_token_secret = oauth1_user_handler.get_access_token(oauth_verifier)
        return access_token, access_token_secret

    def get_me(self, access_token, access_token_secret):
        """_summary_:
        Get user info from twitter api

        Args:
            access_token (_type_): _users_token_
            access_token_secret (_type_): _users_token_secret_

        Returns:
            _object_: _objects container user information_
        """
        try:
            client = tweepy.Client(consumer_key=self.api_key, consumer_secret=self.api_secret, access_token=access_token, access_token_secret=access_token_secret)
            info = client.get_me(user_auth=True, user_fields=['profile_image_url', 'created_at'])
            return info
        except Exception as e:
            print(e)
            return None
        
    def get_profile_image_url(self, twitter_handle):
        """_summary_:
        Get user profile image url

        Args:
            twitter_handle (_str_): _users_twitter_handle_

        Returns:
            _str_: _url_
        """
        try:
            client = tweepy.Client(consumer_key=self.api_key, consumer_secret=self.api_secret, access_token=self.access_token, access_token_secret=self.access_token_secret, bearer_token=self.bearer_token)
            info = client.get_user(username=twitter_handle, user_auth=True, expansions='pinned_tweet_id')
            user = client.get_user(id = info.data.id,user_auth=True, user_fields=['profile_image_url', 'description'])
            return user.data.profile_image_url, user.data.description, user.data.name
        except Exception as e:
            print(e)
            return None