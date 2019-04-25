from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User

from test_blog.settings import EMAIL_HOST_USER

# Create your models here.

class Blog(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    #post = models.ManyToManyField(Post, null=True)
    subscribers = models.ManyToManyField(User)

    def make_owner_as_json(self):
        context = {}
        for key, value in self.owner.__dict__.items():
            if key != "_state":
                context[key] = value
        return context

    def as_json(self):
        context = {}
        for key, value in self.__dict__.items():
            if key != "_state":
                context[key] = value
        context["owner"] = self.make_owner_as_json() 
        return context


class Post(models.Model):
    title = models.CharField(max_length=100, blank=False)
    text = models.TextField(max_length=10000)
    date = models.DateTimeField(auto_now=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blog")

    def email_notification(self, email):
        send_mail(subject="New post in your favorite blog site",
            message="New post in by {}, called {}".format(self.blog.owner, self.title),
            from_email=EMAIL_HOST_USER,
            recipient_list=email if isinstance(email, list) else [email]
            )

    def save(self):
        super().save()
        subs = self.blog.subscribers.all()
        subs_emails = list(sub.email for sub in subs)
        self.email_notification(subs_emails)
        for sub in subs:
            News.objects.create(user=sub, post=self, marked=0)
        #news = News.objects.filter(post__id=self.id)

    def as_json(self):
        context = {}
        for key, value in self.__dict__.items():
            if key != "_state":
                context[key] = value
        context["blog"] = self.blog.as_json() 
        return context


marked_choices = (
    (0, "unread"),
    (1, "read"),
    )

class News(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
    marked = models.IntegerField(default=0, choices=marked_choices)

    def as_json(self):
        context = {}
        for key, value in self.__dict__.items():
            if key != "_state":
                context[key] = value
        context["post"] = self.post.as_json() 
        return context


