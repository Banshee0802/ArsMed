from django.urls import path
from .views import (
                    CustomSignupView, ProfileView, ScheduleCreateView, 
                    ScheduleListView, AvailableScheduleListView, 
                    book_appointment, ScheduleRequestsView,
                    confirm_request, cancel_request,
                    MyAppointmentsView, ScheduleUpdateView,
                    ScheduleDeleteView,
)

app_name = 'users'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile/schedules/', ScheduleListView.as_view(), name="admin_schedule_list"),
    path('profile/schedules/add/', ScheduleCreateView.as_view(), name="admin_schedule_add"),
    path('profile/schedules/<int:pk>/edit/', ScheduleUpdateView.as_view(), name="admin_schedule_edit"),
    path('profile/schedules/<int:pk>/delete/', ScheduleDeleteView.as_view(), name="admin_schedule_delete"),
    path('profile/appointments/', AvailableScheduleListView.as_view(), name="available_schedule"),
    path('book/<int:slot_id>/', book_appointment, name='book_appointment'),
    path('profile/schedules/requests/', ScheduleRequestsView.as_view(), name="schedule_requests"),
    path('profile/schedules/requests/<int:pk>/confirm/', confirm_request, name="confirm_request"),
    path('profile/schedules/requests/<int:pk>/cancel/', cancel_request, name="cancel_request"),
    path('profile/my-appointments/', MyAppointmentsView.as_view(), name="my_appointments"),
    
]
