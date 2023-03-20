from django.db import models
from tinymce import models as tinymce_models
from sorl.thumbnail import ImageField
from django.utils.text import slugify
from twitter_api.twitter_api import TwitterAPI
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
import shortuuid



# Create your models here.

class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.oauth_token

class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255, unique=True)
    screen_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    profile_image_url = models.CharField(max_length=255, null=True)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    followers = models.PositiveIntegerField(default=None, null=True, blank=True)
    account_months = models.PositiveIntegerField(default=None, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    eth_wallet_id = models.CharField(max_length=42, null=True, blank=True)
    sol_wallet_id = models.CharField(max_length=44, null=True, blank=True)
    
    def __str__(self):
        return self.screen_name

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.name)
    
    @classmethod
    def get_default_pk(cls):
        return cls.objects.first().pk
        
class BlogPost(models.Model):
    twitter = models.CharField(max_length=255, null=True, blank=True, help_text='@username')
    title = models.CharField(max_length=255, unique=True, blank=True, null=True)
    slug = models.SlugField(default=None, null=True, editable=False, unique=True)
    thumbnail = ImageField(upload_to='media/uploads/', blank=True, null=True)
    description = models.TextField(blank=True, help_text='Leave blank to populate from twitter profile')
    content = RichTextUploadingField(config_name='awesome_ckeditor', blank=True, null=True)
    default_likes = models.IntegerField(default=0, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=Category.get_default_pk, help_text='Verify this is the same as the category name in the blog post')
    liked_by = models.ManyToManyField(TwitterUser, related_name='liked_by', blank=True)

    def __str__(self):
        return str(self.title)

    def pub_date_pretty(self):
        return self.date.strftime('%b %e %Y')
    
    def get_absolute_url(self):
        return f"/blog/{self.slug}"
    
    def handle_twitter(self):
        twitter_api = TwitterAPI()
        username = self.twitter.replace('@', '')
        try:
            url, description, name = twitter_api.get_profile_image_url(username)
            url = url.replace('_normal', '')
        except:
            raise ValidationError('Error getting twitter profile image and description')
        
        try: 
            self.thumbnail.url
        except:
            self.thumbnail = url
        if description is not None:
            self.description = description
        if self.title is None:
            self.title = name

    def clean(self):
        if self.twitter is not None:
            if self.twitter[1:].isalnum() is False:
                raise ValidationError('Twitter handle must be alphanumeric')
            #check if twitter handle was changed
            obj = BlogPost.objects.filter(id=self.id).first()
            if obj is not None and self.twitter is not None:
                if obj.twitter != self.twitter or self.description == '' or self.title is None or self.thumbnail.name == '' :  
                    #get twitter profile image
                    self.handle_twitter()    
                else:
                    pass
            elif obj is None and self.twitter is not None:
                self.handle_twitter()
            

        

    def save(self, *args, **kwargs):
        if not self.slug:
            #while slug is already in use add the count to the end of the slug
            slug = slugify(self.title)
            count = BlogPost.objects.filter(title=self.title).count()
            if count > 0:
                slug = f"{slug}-{shortuuid.uuid()}"
            self.slug = slug

        super().save(*args, **kwargs)
    

