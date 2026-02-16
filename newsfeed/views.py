import json

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.contants.common import COMMENT_VERB
from friends.models import CustomNotification
from .forms import PostCreateForm
from .models import Post


class PostCreateView(CreateView):
    model = Post
    http_method_names = ['post']
    form_class = PostCreateForm
    template_name = 'home.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return redirect(reverse_lazy('core:home'))

    def post(self, *args, **kwargs):
        form = self.get_form()
        self.object = None
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def create_comment(request, post_id=None):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)

        # إنشاء إشعار في قاعدة البيانات فقط
        CustomNotification.objects.create(
            recipient=post.user,
            actor=request.user,
            verb=COMMENT_VERB,
            description="commented on your post"
        )

        return redirect(reverse_lazy('core:home'))

    return redirect(reverse_lazy('core:home'))
