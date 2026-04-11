from django.urls import path

from .views import (
    chat_view,
    clear_conversation_view,
    stream_view,
    suggested_questions_view,
)


urlpatterns = [
    path("", chat_view, name="chat"),
    path("stream/", stream_view, name="stream"),
    path("suggested-questions/", suggested_questions_view, name="suggested_questions"),
    path("clear-conversation/", clear_conversation_view, name="clear_conversation"),
]
