from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import JsonResponse

from .models import *
# Create your views here.

class BlogerLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def get_user(self, **kwargs):
        user = None
        if "pk" in kwargs or "id" in kwargs:
            pk=kwargs["id"] if "id" in kwargs else kwargs["pk"]
            try:
                user = User.objects.get(pk=pk)
            except Exception as exc:
                print("No user with current id ", pk)
        else:
            try:
                user = User.objects.get(pk=self.request.user.id)
            except Exception as exc:
                # seems like never get it error
                print("No such user")
        return user

    def get_user_blog(self):
        user = self.get_user()
        print("User", user)
        blog = Blog.objects.filter(owner=user)
        print(blog)
        return blog.last() if blog else None                


class HomeView(BlogerLoginRequiredMixin, ListView):
    model = Post
    ordering = "-date"
    template_name = "userspace/home.html"
    context_object_name = "posts"

    def get_queryset(self):
        blog = self.get_user_blog()
        queryset = Post.objects.filter(blog=blog).order_by(self.ordering)
        print("queryset", queryset)
        return queryset


class AjaxResponseView(View):

    def dispatch(self, request, *args, **kwargs):
        return self.render_to_ajax_response(request, *args, **kwargs)

    def get_data(self, request, *args, **kwargs):
        context = {}
        return context

    def render_to_ajax_response(self, request, *args, **kwargs):
        return JsonResponse(self.get_data(request, *args, **kwargs))


class NewsBarView(BlogerLoginRequiredMixin, AjaxResponseView):
    
    def get_data(self, request, *args, **kwargs):
        context = {"status": 400}
        user = self.get_user()
        pk = request.POST.get("id", False)
        if pk:
            try:
                n = News.objects.get(pk=pk)
            except Exception as exc:
                print("No such news")
            else:
                n.marked = 1
                n.save()
        queryset = News.objects.filter(user=user, marked=0).order_by("post")
        if queryset:
            context["news"] = [q.as_json() for q in queryset]
            context["status"] = 200
        return context


class Subscribe(BlogerLoginRequiredMixin, AjaxResponseView):

    def get_data(self, request, *args, **kwargs):
        pk = request.POST.get("id", False)
        subscribe = int(request.POST.get("subscribe", False))
        print(subscribe)
        user = self.get_user()
        if pk:
            try:
                blog = Blog.objects.get(pk=pk)
            except Exception as exc:
                print("Can't get blog by id")
                return {"status": 400, "message": "No such blog"}
            else:
                if subscribe:
                    print("in if")
                    blog.subscribers.add(user)
                else:
                    print("in else")
                    blog.subscribers.remove(user)
                blog.save()
                print(blog.subscribers.all())
                return {"status": 200, "message": "Changed subscribtion"}
        print("Can't get blog by id")
        return {"status": 400, "message": "No such blog"}


class BlogsList(BlogerLoginRequiredMixin, AjaxResponseView):

    def get_data(self, request, *args, **kwargs):
        user = self.get_user()
        unsub = Blog.objects.exclude(subscribers__in=[user])
        sub_in= Blog.objects.filter(subscribers__in=[user])
        return {'status': 200,
            "blogs_in": [q.as_json() for q in sub_in],
            "blogs_out": [q.as_json() for q in unsub]
            }

