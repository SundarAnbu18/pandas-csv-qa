# Django, explained with this chat app

A beginner's walkthrough. Every idea here is used by the chat UI in this repo,
so you can read the explanation and then open the real file.

## Run it

```bash
source .venv/bin/activate
python manage.py runserver
```

Open http://localhost:8000 and ask a question about the employee data.

---

## 1. The big idea

Django is a **request → response** machine. Someone opens a URL, Django finds
the right Python function, that function returns an HTML page.

```
browser asks for "/"
        ↓
chatsite/urls.py     "who handles this address?"
        ↓
chat/urls.py         "the chat view does"
        ↓
chat/views.py        Python runs: read the database, call the AI
        ↓
chat/templates/…     HTML is filled in with the data
        ↓
browser shows the page
```

Learn those five boxes and you know Django.

---

## 2. Project vs app

| | What it is | Here |
| --- | --- | --- |
| **Project** | The whole website. Holds settings. | `chatsite/` |
| **App** | One feature. A project can have many. | `chat/` |

They were created with:

```bash
django-admin startproject chatsite .
python manage.py startapp chat
```

A new app does nothing until you list it in `INSTALLED_APPS` inside
[chatsite/settings.py](chatsite/settings.py). That is a very common beginner
mistake — the app exists but Django never looks at it.

---

## 3. The files, one by one

### `manage.py`
Not code you edit. It is the remote control:

```bash
python manage.py runserver        # start the dev server
python manage.py makemigrations   # "I changed models.py, write the plan"
python manage.py migrate          # "now apply the plan to the database"
python manage.py createsuperuser  # make a login for /admin/
python manage.py shell            # a Python prompt that knows your models
```

### `chatsite/settings.py` — the settings
One big file of variables. The three lines that matter for this app:

```python
INSTALLED_APPS = [..., 'chat']            # turn our app on
DATABASES = {... 'sqlite3' ...}           # a database in one file, db.sqlite3
load_dotenv(BASE_DIR / '.env')            # so the AI can read ANTHROPIC_API_KEY
```

### `chatsite/urls.py` — the main address book
Django checks this first for every request.

```python
path('admin/', admin.site.urls),
path('', include('chat.urls')),   # hand "/" over to the chat app
```

`include()` keeps this file short — each app owns its own URLs.

### `chat/urls.py` — the app's addresses

```python
path('', views.chat, name='chat'),
path('clear/', views.clear, name='clear'),
```

`name='chat'` is a **nickname**. In the template you write `{% url 'clear' %}`
instead of typing `/clear/`. If you later change the address, the template
still works.

### `chat/models.py` — the database table
One class = one table. One attribute = one column.

```python
class Message(models.Model):
    question   = models.TextField()
    answer     = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

You never write SQL. Django does:

```python
Message.objects.create(question=q, answer=a)   # INSERT
Message.objects.all()                          # SELECT *
Message.objects.all().delete()                 # DELETE
Message.objects.filter(question__contains="salary")
```

**Rule to memorise:** change `models.py` → run `makemigrations` then `migrate`.
A migration is a numbered file (`chat/migrations/0001_initial.py`) recording
how the table changed, so your database can catch up step by step.

### `chat/views.py` — the brain
A view takes a `request` and returns a response.

```python
def chat(request):
    if request.method == 'POST':          # user pressed Send
        question = request.POST['question']
        answer = answer_question_from_csv(question)
        Message.objects.create(question=question, answer=answer)
        return redirect('chat')           # ← important, see below

    messages = Message.objects.all()      # user just opened the page
    return render(request, 'chat/chat.html', {'messages': messages})
```

Two things worth understanding:

- **GET vs POST.** GET = "show me the page." POST = "here is form data, do
  something." The same function handles both by checking `request.method`.
- **Redirect after POST.** After saving, we send the browser to a fresh GET.
  Without it, pressing F5 would re-send the question and ask the AI twice.

### `chat/templates/chat/chat.html` — the page
HTML with a small template language mixed in:

| Syntax | Meaning |
| --- | --- |
| `{{ message.question }}` | print a value |
| `{% for m in messages %}` … `{% endfor %}` | loop |
| `{% empty %}` | runs when the list is empty |
| `{% if error %}` | condition |
| `{% url 'clear' %}` | build a URL from its nickname |
| `{% csrf_token %}` | **required** inside every POST form |

Without `{% csrf_token %}` Django blocks the form with a 403 error. It is a
security check that proves the form came from your own site.

Templates live in `chat/templates/chat/` — the app name appears twice on
purpose, so two apps can both have a `chat.html` without clashing.

### `chat/ai.py` — the LangChain part
Not a Django file at all. Keeping the AI code out of `views.py` means the view
stays about the web, and this file can be tested on its own:

```bash
python lauch.py "How many employees are in department 50?"
```

### `chat/admin.py` — a free admin panel
Registering `Message` there gives you a working UI at
http://localhost:8000/admin/ to browse and delete rows. Create a login first:

```bash
python manage.py createsuperuser
```

---

## 4. Follow one click all the way through

You type *"Who has the highest salary?"* and press Send.

1. Browser sends `POST /` with `question=Who has the highest salary?`
2. `chatsite/urls.py` → `chat/urls.py` → `views.chat(request)`
3. `request.method == 'POST'`, so the view reads `request.POST['question']`
4. `answer_question_from_csv()` puts the CSV plus your question in a prompt and
   calls Claude (this is the slow part, a few seconds)
5. `Message.objects.create(...)` writes one row into `db.sqlite3`
6. `redirect('chat')` tells the browser "go to / again"
7. Browser sends `GET /`, the view loads all messages and renders the template
8. You see both bubbles

---

## 5. Things to try next

Small changes, in increasing difficulty:

1. Show the time under each message — `{{ message.created_at }}` in the template.
2. Add a `models.BooleanField(default=False)` called `starred` to `Message`,
   then run `makemigrations` + `migrate`. Watch the migration file appear.
3. Make the page only show the last 10 messages: `Message.objects.all()[:10]`
   (careful — `ordering` is oldest-first, so you may want `.order_by('-created_at')`).
4. Replace the plain `<input>` with a Django **Form** class (`forms.py`) — this
   is how real Django projects validate input.
5. Send the question with `fetch()` in JavaScript instead of a form submit, so
   the page does not reload. That is the step toward a modern chat UI.

---

## 6. Errors you will hit, and what they mean

| Error | Cause |
| --- | --- |
| `TemplateDoesNotExist` | Wrong path, or the app is not in `INSTALLED_APPS` |
| `no such table: chat_message` | You forgot `python manage.py migrate` |
| `CSRF verification failed` | Missing `{% csrf_token %}` in the form |
| `NoReverseMatch` | `{% url 'x' %}` but no `name='x'` in urls.py |
| `You have unapplied migrations` | Run `migrate` |
| Page hangs a few seconds | Normal — the AI call is slow, the button says "Thinking…" |
