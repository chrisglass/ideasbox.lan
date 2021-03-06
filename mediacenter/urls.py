from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^document/(?P<pk>[\d]+)/$', views.document_detail,
        name='document_detail'),
    url(r'^document/(?P<pk>[\d]+)/edit/$', views.document_update,
        name='document_update'),
    url(r'^document/(?P<pk>[\d]+)/delete/$', views.document_delete,
        name='document_delete'),
    url(r'^document/new/$', views.document_create, name='document_create'),
]
