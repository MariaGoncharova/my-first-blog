from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^post/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
    url('drafts/', views.post_draft_list, name='post_draft_list'),
    url(r'^post/(?P<pk>\d+)/publish/', views.post_publish, name='post_publish'),
    url(r'^post/(?P<pk>\d+)/remove/', views.post_remove, name='post_remove'),
    # url(r'^post/(?P<pk>\d+)/comment/$', views.add_comment_to_post, name='add_comment_to_post'),
    url(r'^post/(?P<pk>\d+)/comment/$', views.create_comment, name='create_comment'),
    url(r'^tests$', views.tests_list, name='tests'),
    url(r'^test/(?P<pk>\d+)$', views.render_test, name='test'),
    url(r'^my-tests/$', views.get_my_tests, name='my_tests'),

    # path('profile/', views.TestView, name='user_tests'),

    url(r'^check-pannel/user-list$', views.get_user_list, name='user_lists'),
    url(r'^check-pannel/user-tests/(?P<user>\d+)/$', views.get_user_tests, name='user-tests'),
    url(r'^check-pannel/resolve-test/(?P<attempt>\d+)/$', views.resolve_test, name='resolve-test'),

    # url(r'^profile/(?P<username>[0-9A-Za-z_]+)/$', views.profile, name='profile'),
]
