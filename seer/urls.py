from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('search/', views.search, name='search'),
    path('query', views.pre_query, name='pre_query'),
    path('', views.search, name='search2'),
    path('about/', views.about, name='about'),
    path('contact-us', views.contact_us, name='contact_us'),
    path('contact', views.store, name='store'),
    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('data', views.data, name='data'),
    path('publications', views.publications, name='publications'),
    path('news', views.news, name="news"),
    path('people', views.people, name="people"),
    path('visualizations', views.visualizations, name="visualizations"),
    re_path(r'robots\.txt', views.robots, name='robots')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
