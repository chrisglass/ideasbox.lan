import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from ideasbox.blog.tests.factories import ContentFactory
from ideasbox.blog.models import Content
from ideasbox.library.tests.factories import BookSpecimenFactory

from ..views import ByTag

pytestmark = pytest.mark.django_db
user_model = get_user_model()


def test_home_page(app):
    assert app.get('/')


def test_anonymous_user_should_not_access_admin(app):
    response = app.get(reverse('admin:index'), status=302)
    assert 'login' in response['Location']


def test_normal_user_should_not_access_admin(loggedapp, user):
    response = loggedapp.get(reverse('admin:index'), status=302)
    assert 'login' in response['Location']


def test_staff_user_should_access_admin(staffapp):
    assert staffapp.get(reverse('admin:index'), status=200)


def test_login_page_should_return_form_in_GET_mode(app):
    assert app.get(reverse('login'), status=200)


def test_login_page_should_log_in_user_if_POST_data_is_correct(client, user):
    response = client.post(reverse('login'), {
        'username': user.serial,
        'password': 'password'
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 1
    assert response.context['user'].is_authenticated()


def test_login_page_should_not_log_in_user_with_incorrect_POST(client, user):
    response = client.post(reverse('login'), {
        'username': user.serial,
        'password': 'passwordxxx'
    }, follow=True)
    assert response.status_code == 200
    assert len(response.redirect_chain) == 0
    assert not response.context['user'].is_authenticated()


def test_user_list_page_should_be_accessible(app, user):
    response = app.get(reverse('user_list'))
    response.mustcontain(unicode(user))


def test_user_detail_page_should_be_accessible(app, user):
    response = app.get(reverse('user_detail', kwargs={'pk': user.pk}))
    response.mustcontain(unicode(user))


def test_user_create_page_should_not_be_accessible_to_anonymous(app):
    assert app.get(reverse('user_create'), status=302)


def test_non_staff_should_not_access_user_create_page(loggedapp, user):
    assert loggedapp.get(reverse('user_create'), status=302)


def test_user_create_page_should_be_accessible_to_staff(staffapp):
    assert staffapp.get(reverse('user_create'), status=200)


def test_should_create_user_with_serial_only(staffapp):
    assert len(user_model.objects.all()) == 1
    serial = '12345xz22'
    form = staffapp.get(reverse('user_create')).forms['model_form']
    form['serial'] = serial
    form.submit()
    assert len(user_model.objects.all()) == 2
    assert user_model.objects.filter(serial=serial)


def test_should_not_create_user_without_serial(staffapp):
    assert len(user_model.objects.all()) == 1
    form = staffapp.get(reverse('user_create')).forms['model_form']
    form.submit()
    assert len(user_model.objects.all()) == 1


def test_user_update_page_should_not_be_accessible_to_anonymous(app, user):
    assert app.get(reverse('user_update', kwargs={'pk': user.pk}), status=302)


def test_non_staff_should_not_access_user_update_page(loggedapp, user):
    assert loggedapp.get(reverse('user_update', kwargs={'pk': user.pk}),
                         status=302)


def test_staff_should_access_user_update_page(staffapp, user):
    assert staffapp.get(reverse('user_update', kwargs={'pk': user.pk}),
                        status=200)


def test_staff_should_be_able_to_update_user(staffapp, user):
    assert len(user_model.objects.all()) == 2
    url = reverse('user_update', kwargs={'pk': user.pk})
    short_name = 'Denis'
    form = staffapp.get(url).forms['model_form']
    form['serial'] = user.serial
    form['short_name'] = short_name
    form.submit().follow()
    assert len(user_model.objects.all()) == 2
    assert user_model.objects.get(serial=user.serial).short_name == short_name


def test_should_not_update_user_without_serial(app, staffapp, user):
    url = reverse('user_update', kwargs={'pk': user.pk})
    form = staffapp.get(url).forms['model_form']
    form['serial'] = ''
    form['short_name'] = 'ABCDEF'
    assert form.submit()
    dbuser = user_model.objects.get(serial=user.serial)
    assert dbuser.short_name == user.short_name


def test_delete_page_should_not_be_reachable_to_anonymous(app, user):
    assert app.get(reverse('user_delete', kwargs={'pk': user.pk}), status=302)


def test_delete_page_should_not_be_reachable_to_non_staff(loggedapp, user):
    assert loggedapp.get(reverse('user_delete', kwargs={'pk': user.pk}),
                         status=302)


def test_staff_user_should_access_confirm_delete_page(staffapp, user):
    assert staffapp.get(reverse('user_delete', kwargs={'pk': user.pk}),
                        status=200)


def test_anonymous_cannot_delete_user(app, user):
    assert len(user_model.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': user.pk})
    url = reverse('user_delete', kwargs={'pk': user.pk})
    assert app.get(url, status=302)
    assert len(user_model.objects.all()) == 1


def test_non_staff_cannot_delete_user(loggedapp, user):
    assert len(user_model.objects.all()) == 1
    url = reverse('user_delete', kwargs={'pk': user.pk})
    assert loggedapp.get(url, status=302)
    assert len(user_model.objects.all()) == 1


def test_staff_user_can_delete_user(staffapp, user):
    assert len(user_model.objects.all()) == 2  # staff user and normal user
    url = reverse('user_delete', kwargs={'pk': user.pk})
    form = staffapp.get(url).forms['delete_form']
    form.submit()
    assert len(user_model.objects.all()) == 1


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = ContentFactory(status=Content.PUBLISHED, tags=['plane'])
    boat = ContentFactory(status=Content.PUBLISHED, tags=['boat'])
    plane2 = BookSpecimenFactory(book__tags=['plane'])
    boat2 = BookSpecimenFactory(book__tags=['boat'])
    response = app.get(reverse('by_tag', kwargs={'tag': 'plane'}))
    assert plane.title in response.content
    assert plane2.book.title in response.content
    assert boat.title not in response.content
    assert boat2.book.title not in response.content


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(ByTag, 'paginate_by', 2)
    ContentFactory.create_batch(size=2, status=Content.PUBLISHED,
                                tags=['plane'])
    BookSpecimenFactory.create_batch(size=2, book__tags=['plane'])
    url = reverse('by_tag', kwargs={'tag': 'plane'})
    response = app.get(url)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url + '?page=3', status=404)
