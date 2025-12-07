from django.urls import path
from .views import CustomSignupView, ProfileView, ScheduleCreateView, ScheduleListView, AvailableScheduleListView, book_appointment

app_name = 'users'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile/schedules/', ScheduleListView.as_view(), name="admin_schedule_list"),
    path('profile/schedules/add/', ScheduleCreateView.as_view(), name="admin_schedule_add"),
    path('profile/appointments/', AvailableScheduleListView.as_view(), name="available_schedule"),
    path('book/<int:slot_id>/', book_appointment, name='book_appointment'),
]
