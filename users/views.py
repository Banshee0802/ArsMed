from datetime import datetime, timedelta
import uuid
from django.utils import timezone
from django.shortcuts import redirect, render
from allauth.account.views import SignupView
from django.views.decorators.http import require_POST
from core.signals import send_confirmation_email
from .forms import AdminPatientForm, CustomSignupForm, ProfileForm, ScheduleForm
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.models import Schedule, Doctor
from users.models import CustomUser
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from core.utils.telegram import send_telegram_message


# Helper для фильтрации врачей в списке
def get_available_slots_queryset(doctor_slug=None):
    today = timezone.localdate()
    current_time = timezone.localtime().time()

    qs = (
        Schedule.objects.filter(
            Q(date__gt=today) | Q(date=today, start_time__gt=current_time),
            status="available",
        )
        .select_related("doctor")
        .order_by("doctor_id", "date", "start_time")
    )

    if doctor_slug:
        qs = qs.filter(doctor__slug=doctor_slug)

    return qs


# Функция для группировки врачей
def group_slots_by_doctor_and_date(slots):
    doctors = {}
    for slot in slots:
        doc_id = slot.doctor.id
        doctors.setdefault(doc_id, {"doctor": slot.doctor, "dates": {}})
        doctors[doc_id]["dates"].setdefault(slot.date, []).append(slot)
    return doctors


# Кастомная регистрация пациента
class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "На ваш email отправлено письмо с подтверждением."
        )
        return response


# Вьюшка профиля пациента
class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileForm
    template_name = "profile/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Подписка обновлена")
        return super().form_valid(form)


# Миксин для админ-прав
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# Список расписаний врачей для админа
class ScheduleListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Schedule
    template_name = "admin_panel/admin_schedule_list.html"
    context_object_name = "schedules"

    # Все графики и сортировка
    def get_queryset(self):
        qs = Schedule.objects.select_related("doctor", "booked_by").order_by(
            "doctor__last_name", "date", "start_time"
        )

        doctor = self.request.GET.get("doctor")
        date = self.request.GET.get("date")
        status = self.request.GET.get("status")

        if doctor:
            qs = qs.filter(doctor_id=doctor)
        if date:
            qs = qs.filter(date=date)
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["doctors"] = Doctor.objects.all()
        context["status_choices"] = Schedule.STATUS_CHOICES

        return context


# Декоратор: только админ (для подсчета запросов)
@user_passes_test(lambda u: u.is_staff)
def new_requests_count_api(request):
    count = Schedule.objects.filter(status="booked").count()
    return JsonResponse({"count": count})


# Создание расписания врачей
class ScheduleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "admin_panel/admin_schedule_form.html"
    success_url = reverse_lazy("users:admin_schedule_list")

    # При валидной форме - разбиение слотов по 30 минут
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
                    status="available",
                )
            )
            start += timedelta(minutes=30)

        Schedule.objects.bulk_create(slots)
        return redirect(self.success_url)


# Редактирование слота врача + запись пациента
class ScheduleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "admin_panel/admin_schedule_edit.html"
    success_url = reverse_lazy("users:admin_schedule_list")

    def form_valid(self, form):
        old_appointment = Schedule.objects.get(pk=self.object.pk)

        appointment = form.save(commit=False)

        if appointment.status == "available":
            appointment.booked_by = None

        if appointment.medical_report and appointment.status != "completed":
            appointment.status = "completed"
            appointment.completed_at = timezone.now()

        appointment.save()

        if appointment.status == "confirmed":
            if (
                not old_appointment.booked_by
                or old_appointment.booked_by != appointment.booked_by
            ):
                send_confirmation_email(appointment)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient_form"] = AdminPatientForm()
        return context


# Удаление отдельного слота по времени
class ScheduleDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Schedule
    template_name = "admin_panel/admin_schedule_delete.html"
    success_url = reverse_lazy("users:admin_schedule_list")


# Расписание врачей для авторизованного пациента
class AvailableScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    template_name = "profile/available_schedule.html"
    context_object_name = "schedules"

    # Доступные слоты
    def get_queryset(self):
        doctor_slug = self.kwargs.get("doctor_slug")
        return get_available_slots_queryset(doctor_slug)

    # Группировка по врачам
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        slots = self.get_queryset()

        context["doctors"] = group_slots_by_doctor_and_date(slots)
        return context


# Подтверждение записи при выборе времени
def confirm_appointment_view(request, slot_id):
    slot = get_object_or_404(Schedule, id=slot_id, status="available")

    return render(request, "profile/confirm_appointment.html", {"slot": slot})


# Запись пациента на слот + уведомление для админа в тг
def book_appointment(request, slot_id):
    slot = get_object_or_404(Schedule, id=slot_id, status="available")
    slot.booked_by = request.user
    slot.status = "booked"
    slot.save()

    patient_name = " ".join(
        [
            request.user.last_name.capitalize(),
            request.user.first_name.capitalize(),
            request.user.patronymic.capitalize() if request.user.patronymic else "",
        ]
    )

    send_telegram_message(
        f"🩺 <b>Новая запись</b>\n"
        f"Пациент: {patient_name}\n"
        f"Номер телефона: {request.user.phone}\n"
        f"Врач: {slot.doctor}\n"
        f"Дата: {slot.date}\n"
        f"Время: {slot.start_time}"
    )

    messages.success(
        request, f"Вы записаны к {slot.doctor} на {slot.date} в {slot.start_time}"
    )
    return redirect("users:my_appointments")


# Запросы на запись
class ScheduleRequestsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Schedule
    template_name = "admin_panel/schedule_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        return Schedule.objects.filter(status="booked").order_by("date", "start_time")


# Подтверждение записи админом + отправка email пациенту о подтверждении
def confirm_request(request, pk):
    slot = get_object_or_404(Schedule, id=pk)
    if slot.status != "confirmed":
        slot.status = "confirmed"
        slot.save()

        send_confirmation_email(slot)

    messages.success(request, "Запись подтверждена")
    return redirect("users:schedule_requests")


# Отмена записи админом
def cancel_request(request, pk):
    slot = get_object_or_404(Schedule, id=pk)
    slot.status = "available"
    slot.booked_by = None
    slot.save()
    messages.success(request, "Запись отменена")
    return redirect("users:schedule_requests")


# Записи пациента к врачам + завершенные записи
class MyAppointmentsView(LoginRequiredMixin, ListView):
    model = Schedule
    template_name = "profile/my_appointments.html"
    context_object_name = "appointments"

    # Будущие приёмы
    def get_queryset(self):
        today = timezone.localdate()
        return Schedule.objects.filter(
            booked_by=self.request.user, date__gte=today
        ).order_by("date", "start_time")

    # Завершенные приёмы
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upcoming, past = get_patient_appointments(self.request.user)

        context["upcoming_appointments"] = upcoming
        context["past_appointments"] = past

        return context


# Получение записи пациентов к врачам (для списка пациентов)
def get_patient_appointments(user):
    today = timezone.now().date()

    upcoming = Schedule.objects.filter(
        booked_by=user, status__in=["confirmed", "booked"], date__gte=today
    ).order_by("date", "start_time")

    past = Schedule.objects.filter(
        booked_by=user, status__in=["completed", "cancelled"]
    ).order_by("-date", "-start_time")

    return upcoming, past


# Список пациентов
class AdminPatientsListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = "admin_panel/patients_list.html"
    context_object_name = "patients"

    # Фильтр пациентов по поиску
    def get_queryset(self):
        queryset = CustomUser.objects.filter(role="patient")

        query = self.request.GET.get("q")
        if query:
            query = query.lower().strip()
        if query:
            queryset = queryset.filter(
                Q(last_name__icontains=query)
                | Q(first_name__icontains=query)
                | Q(phone__icontains=query)
            )

        return queryset.order_by("last_name", "first_name")  # Сортировка

    # Запрос поиска
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


# Детальная карточка пациента
class AdminPatientDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = CustomUser
    template_name = "admin_panel/patient_detail.html"
    context_object_name = "patient"

    # Записи пациента к врачам
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upcoming, past = get_patient_appointments(self.object)

        context["upcoming_appointments"] = upcoming
        context["past_appointments"] = past

        return context


# Закрытие/открытие смены врача
@require_POST
@user_passes_test(lambda u: u.is_staff)
def toggle_day_status(request):
    doctor_id = request.POST.get("doctor")
    date_str = request.POST.get("date")
    action = request.POST.get("action")

    if not doctor_id or not date_str or action not in ("close", "open"):
        messages.error(request, "Некорректные данные")
        return redirect("users:admin_schedule_list")

    new_status = "closed" if action == "close" else "available"

    updated = (
        Schedule.objects.filter(doctor_id=doctor_id, date=date_str)
        .exclude(status="booked")
        .exclude(status="confirmed")
        .update(status=new_status)
    )

    msg = f"Смена {date_str} {'закрыта' if action == 'close' else 'открыта'} ({updated} слотов)"
    messages.success(request, msg) if updated else messages.info(
        request, "Нечего менять"
    )

    return redirect("users:admin_schedule_list")


# Поиск пациента по базе при редактировании слота врача (для записи)
class SearchPatientsView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        q = request.GET.get("q", "").strip()
        if len(q) < 2:
            return JsonResponse({"results": []})

        patients = CustomUser.objects.filter(role="patient").filter(
            Q(last_name__icontains=q)
            | Q(first_name__icontains=q)
            | Q(patronymic__icontains=q)
            | Q(phone__icontains=q)
        )[:20]

        results = [
            {
                "id": p.id,
                "text": f"{p.last_name or ''} {p.first_name or ''} {p.patronymic or ''} | {p.phone or '-'} | {p.birth_date or '-'}",
            }
            for p in patients
        ]
        return JsonResponse({"results": results})


# Создание пациента, если нет в базе
class AdminPatientCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        form = AdminPatientForm()
        return render(
            request, "admin_panel/admin_patient_form.html", {"patient_form": form}
        )

    def post(self, request):
        form = AdminPatientForm(request.POST)

        if not form.is_valid():
            return render(
                request, "admin_panel/admin_patient_form.html", {"patient_form": form}
            )

        user = form.save(commit=False)
        user.role = "patient"
        user.is_active = False
        user.username = f"guest_{user.phone or uuid.uuid4().hex[:8]}"
        user.set_unusable_password()
        user.save()

        schedule_pk = self.request.POST.get("schedule_pk")
        if schedule_pk:
            return redirect("users:admin_schedule_edit", pk=schedule_pk)
        return redirect("users:admin_patients_list")
