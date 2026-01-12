from datetime import date, datetime, timedelta, timezone
from django.utils import timezone
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from .forms import CustomSignupForm, ScheduleForm
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.models import Schedule, Doctor
from users.models import CustomUser
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test


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

     def get_queryset(self):
          qs = Schedule.objects.select_related('doctor', 'booked_by').order_by(
               'doctor__last_name',
               'date',
               'start_time'
          )

          doctor = self.request.GET.get('doctor')
          date = self.request.GET.get('date')
          status = self.request.GET.get('status')

          if doctor:
               qs = qs.filter(doctor_id=doctor)
          if date:
               qs = qs.filter(date=date)
          if status:
               qs = qs.filter(status=status)

          return qs
     
     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
     
          context['doctors'] = Doctor.objects.all()
          context['status_choices'] = Schedule.STATUS_CHOICES

          return context
     

@user_passes_test(lambda u: u.is_staff)
def new_requests_count_api(request):
     count = Schedule.objects.filter(status='booked').count()
     return JsonResponse({'count': count})
          

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
              slots.append(
               Schedule(
               doctor=work_day.doctor,
               date=work_day.date,
               start_time=start.time(),
               end_time=(start + timedelta(minutes=30)).time(),
               status='available'
                    )
               )
              start += timedelta(minutes=30)
         
         Schedule.objects.bulk_create(slots)
         return redirect(self.success_url) 
     

class ScheduleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
     model = Schedule
     form_class = ScheduleForm
     template_name = 'admin_panel/admin_schedule_edit.html'
     success_url = reverse_lazy('users:admin_schedule_list')

     def form_valid(self, form):
         appointment = form.save(commit=False)

         if appointment.medical_report and appointment.status != 'completed':
              appointment.status = 'completed'
              appointment.completed_at = timezone.now()
         appointment.save()
         return super().form_valid(form)
     

class ScheduleDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
     model = Schedule
     template_name = 'admin_panel/admin_schedule_delete.html'
     success_url = reverse_lazy('users:admin_schedule_list')


class AvailableScheduleListView(LoginRequiredMixin, ListView):
     model = Schedule
     template_name = 'profile/available_schedule.html'
     context_object_name = 'schedules'

     def get_queryset(self):
          today = timezone.localdate()
          return Schedule.objects.filter(
             date__gte=today
        ).order_by('date', 'start_time')
     
     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          today = timezone.localdate()

          slots = Schedule.objects.filter(
               status='available',
               date__gte=today
               ).select_related("doctor").order_by('doctor__id', 'date', 'start_time')

          doctors = {}
          for slot in slots:
               doc_id = slot.doctor.id
               if doc_id not in doctors:
                    doctors[doc_id] = {'doctor': slot.doctor, 'dates': {}}

               date_str = slot.date.strftime('%Y-%m-%d')
               if date_str not in doctors[doc_id]['dates']:
                    doctors[doc_id]['dates'][date_str] = []

               doctors[doc_id]['dates'][date_str].append(slot)

          context['doctors'] = doctors
          return context
               

def book_appointment(request, slot_id):
    slot = get_object_or_404(Schedule, id=slot_id, status='available')
    slot.booked_by = request.user
    slot.status = 'booked'
    slot.save()
    messages.success(request, f"Вы записаны к {slot.doctor} на {slot.date} в {slot.start_time}")
    return redirect('users:available_schedule')


class ScheduleRequestsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
     model = Schedule
     template_name = 'admin_panel/schedule_requests.html'
     context_object_name = 'requests'

     def get_queryset(self):
          return Schedule.objects.filter(status='booked').order_by('date', 'start_time')
     

def confirm_request(request, pk):
     slot = get_object_or_404(Schedule, id=pk)
     slot.status = 'confirmed'
     slot.save()
     messages.success(request, "Запись подтверждена")
     return redirect('users:schedule_requests')


def cancel_request(request, pk):
     slot = get_object_or_404(Schedule, id=pk)
     slot.status = 'available'
     slot.booked_by = None
     slot.save()
     messages.success(request, "Запись отменена")
     return redirect('users:schedule_requests')


class MyAppointmentsView(LoginRequiredMixin, ListView):
     model = Schedule
     template_name = 'profile/my_appointments.html'
     context_object_name = 'appointments'


     def get_queryset(self):
        today = timezone.localdate()
        return Schedule.objects.filter(
            booked_by=self.request.user,
            date__gte=today
        ).order_by('date', 'start_time')


     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          
          upcoming, past = get_patient_appointments(self.request.user)

          context['upcoming_appointments'] = upcoming
          context['past_appointments'] = past
 
          return context
     

def get_patient_appointments(user):
     today = timezone.now().date()

     upcoming = Schedule.objects.filter(
          booked_by=user,
          status__in=['confirmed', 'booked'],
          date__gte=today
     ).order_by('date', 'start_time')

     past = Schedule.objects.filter(
          booked_by=user,
          status__in=['completed', 'cancelled']
     ).order_by('-date', '-start_time')

     return upcoming, past


class AdminPatientsListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
     model = CustomUser
     template_name = 'admin_panel/patients_list.html'
     context_object_name = 'patients'

     def get_queryset(self):
          queryset = CustomUser.objects.filter(role='patient')

          query = self.request.GET.get('q')
          if query:
               query = query.lower().strip()
          if query:
               queryset = queryset.filter(
                    Q(last_name__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(phone__icontains=query)
               )

          return queryset.order_by('last_name', 'first_name')

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          context['query'] = self.request.GET.get('q', '')
          return context
     

class AdminPatientDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
     model = CustomUser
     template_name = 'admin_panel/patient_detail.html'
     context_object_name = 'patient'

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)

          upcoming, past = get_patient_appointments(self.object)

          context['upcoming_appointments'] = upcoming
          context['past_appointments'] = past

          return context