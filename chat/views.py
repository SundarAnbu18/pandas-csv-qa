"""A view = a Python function that takes a request and returns a response.

This one function handles both jobs:
  GET  -> just show the chat page with all past messages
  POST -> the user submitted the form, so save + answer, then redirect
"""

from django.shortcuts import redirect, render

from .ai import answer_question_from_csv
from .models import Message


def chat(request):
    error = None

    if request.method == 'POST':
        # request.POST is a dict of the submitted form fields.
        question = request.POST.get('question', '').strip()

        if question:
            try:
                answer = answer_question_from_csv(question)
            except Exception as exc:  # e.g. missing API key, no internet
                error = f"Could not reach the AI: {exc}"
            else:
                # .create() makes a new row in the database and saves it.
                Message.objects.create(question=question, answer=answer)
                # Redirect after a successful POST so refreshing the page
                # does not send the same question twice.
                return redirect('chat')

    # .all() reads every row back (ordered oldest-first, see models.py).
    messages = Message.objects.all()

    # render(request, template, context) turns a template into an HTML page.
    return render(request, 'chat/chat.html', {'messages': messages, 'error': error})


def clear(request):
    """Delete the whole conversation, then go back to the chat page."""
    if request.method == 'POST':
        Message.objects.all().delete()
    return redirect('chat')
