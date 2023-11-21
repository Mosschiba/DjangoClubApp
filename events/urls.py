from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:year>/<str:month>/', views.home, name='home'),
    path('add_venue/', views.add_venue, name='add-venue'),
    path('list_venues/', views.list_venues, name='list-venues'),
    path('show_venue/<venue_id>', views.show_venue, name='show-venue'),
    path('search_venue/', views.search_venue, name="search-venue"),
    path('update_venue/<venue_id>', views.update_venue, name="update-venue"),
    path('delete_venue/<venue_id>', views.delete_venue, name="delete-venue"),    
    path('events/', views.all_events, name='list-events'),
    path('add_event', views.add_event, name="add-event"),
    path('update_event/<event_id>', views.update_event, name="update-event"),
    path('delete_event/<event_id>', views.delete_event, name="delete-event"),
]
