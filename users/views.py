from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from .forms import CustomSignupForm, ScheduleForm
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.models import Schedule, Doctor
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "На ваш email отправлено письмо с подтверждением."
        )
        return response
    

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["user"] = self.request.user
            return context
        

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    

class ScheduleListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
     model = Schedule
     template_name = 'admin_panel/admin_schedule_list.html'
     context_object_name = 'schedules'


class ScheduleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
     model = Schedule
     form_class = ScheduleForm
     template_name = 'admin_panel/admin_schedule_form.html'
     success_url = reverse_lazy('users:admin_schedule_list')

     def form_valid(self, form):
         work_day = form.save(commit=False)
         start = datetime.combine(work_day.date, work_day.start_time)
         end = datetime.combine(work_day.date, work_day.end_time)
         slots = []
         while start < end:
              slots.append (
              Schedule(
                   doctor=work_day.doctor,
                   date=work_day.date,
                   start_time=start.time(),
                   end_time=(start + timedelta(minutes=30)).time(),
                   is_available=True
              )
            )
              start += timedelta(minutes=30)
         
         Schedule.objects.bulk_create(slots)
         return redirect(self.success_url) 


class AvailableScheduleListView(LoginRequiredMixin, ListView):
     model = Schedule
     template_name = 'profile/available_schedule.html'
     context_object_name = 'schedules'

     def get_queryset(self):
          return Schedule.objects.filter(is_available=True, date__gte=date.today()).order_by('date', 'start_time')
     
     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          slots = Schedule.objects.filter(is_available=True).select_related("doctor")

          doctors = {}

          for slot in slots:
               doc = slot.doctor
               date = slot.date

               doctors.setdefault(doc, {})
               doctors[doc].setdefault(date, [])
               doctors[doc][date].append(slot)

          context["doctors"] = doctors
          return context
     

def book_appointment(request, slot_id):
    slot = get_object_or_404(Schedule, id=slot_id, is_available=True)
    slot.booked_by = request.user
    slot.is_available = False
    slot.save()
    messages.success(request, f"Вы записаны к {slot.doctor} на {slot.date} в {slot.start_time}")
    return redirect('users:available_schedule')