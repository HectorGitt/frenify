from django.contrib import admin
from .models import BlogPost, Category

# Register your models here.
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):



    list_display = ('title', 'pub_date_pretty', 'twitter', 'likes')
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_buttons_template'] = 'admin/test.html'
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
    
    def add_view(self, request, form_url = '', extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_buttons_template'] = 'admin/test.html'
        return super().add_view(request, form_url, extra_context)

@admin.register(Category)   
class CategoryAdmin(admin.ModelAdmin):
    pass

