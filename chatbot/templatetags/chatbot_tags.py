from django import template

register = template.Library()


@register.inclusion_tag('chatbot/chatbot_widget.html', takes_context=True)
def chatbot_widget(context):
    """Renders the chatbot widget for authenticated users."""
    request = context.get('request')
    return {
        'show_chatbot': request and request.user.is_authenticated,
    }
