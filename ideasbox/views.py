from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.forms.models import modelform_factory
from django.shortcuts import render
from django.views.generic import (ListView, DetailView, UpdateView, CreateView,
                                  DeleteView)

from taggit.models import TaggedItem

from ideasbox.blog.models import Content
from ideasbox.library.models import Book
from ideasbox.mediacenter.models import Document

user_model = get_user_model()


def index(request):
    contents = Content.objects.published()[:3]
    random_book = Book.objects.available().order_by('?').first()
    random_doc = Document.objects.order_by('?').first()
    context = {
        'blog_contents': contents,
        'random_book': random_book,
        'random_doc': random_doc,
    }
    return render(request, 'index.html', context)


class ByTag(ListView):
    template_name = 'ideasbox/by_tag.html'
    paginate_by = 20

    def get_queryset(self):
        return TaggedItem.objects.filter(tag__slug=self.kwargs['tag'])

by_tag = ByTag.as_view()


class UserList(ListView):
    model = user_model
    template_name = 'ideasbox/user_list.html'
    context_object_name = 'user_list'
user_list = UserList.as_view()


class UserDetail(DetailView):
    model = user_model
    template_name = 'ideasbox/user_detail.html'
    context_object_name = 'user_obj'
user_detail = UserDetail.as_view()


class UserFormMixin(object):
    exclude = ['password', 'last_login']

    def get_form_class(self):
        return modelform_factory(self.model, exclude=self.exclude)


class UserUpdate(UserFormMixin, UpdateView):
    model = user_model
    template_name = 'ideasbox/user_form.html'
    context_object_name = 'user_obj'
user_update = staff_member_required(UserUpdate.as_view())


class UserCreate(UserFormMixin, CreateView):
    model = user_model
    template_name = 'ideasbox/user_form.html'
    context_object_name = 'user_obj'
user_create = staff_member_required(UserCreate.as_view())


class UserDelete(DeleteView):
    model = user_model
    template_name = 'ideasbox/user_confirm_delete.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('user_list')
user_delete = staff_member_required(UserDelete.as_view())
