from django import template

register = template.Library()

register.simple_tag(name='is_liked')

@register.simple_tag(name='is_liked', takes_context=True)
def is_liked(context, value):
    try:
        request = context['request']
        if request.user.is_authenticated and value.is_liked(request.user):
            return True
        else:
            return False
    except:
        return False


