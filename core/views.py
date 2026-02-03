import re
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, View
from core.forms import ReviewForm
from .models import (
    HeroCard,
    Review,
    Schedule,
    SmallCard,
    SquareCard,
    Doctor,
    Services,
    Promotion,
    Contacts,
    SymptomAnalysis,
)
from users.views import get_available_slots_queryset
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages
from django.db.models import Avg
import logging
from django.conf import settings
from gigachat import GigaChat
from django.shortcuts import render


logger = logging.getLogger(__name__)
# ИИ-бот для диагностики симптомов
class SymptomCheckerView(View):
    template_name = "core/symptom_checker.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        user_text = request.POST.get("symptoms", "").strip()
        ai_response = ""
        error_message = None

        if not user_text:
            error_message = "Пожалуйста, опишите Ваши симптомы"
        else:
            try:
                with GigaChat(
                    credentials=settings.GIGACHAT_CREDENTIALS,
                    verify_ssl_certs=True,
                    ca_bundle_file=settings.GIGACHAT_CERTS,
                    scope="GIGACHAT_API_PERS"
                ) as giga:
                    
                    response = giga.chat({
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Ты — медицинский ИИ-ассистент клиники. "
                                    "Твоя задача: проанализировать жалобы пользователя, "
                                    "назвать возможные причины (не ставя окончательный диагноз) "
                                    "и подсказать, к какому врачу (терапевт, ЛОР, хирург и т.д.) записаться. "
                                    "Отвечай вежливо и кратко. В конце обязательно пиши: "
                                    "'Внимание! Это предварительная информация, необходим очный осмотр врача'"
                                    "После этого дисклеймера ОБЯЗАТЕЛЬНО добавь техническую строку строго в формате: "
                                    "ВРАЧ_ДЛЯ_БАЗЫ: [Название специалиста]"
                                )
                            }, 
                            {"role": "user", "content": user_text}
                        ]
                    })
                    ai_response = response.choices[0].message.content

                   
                    match = re.search(r"ВРАЧ_ДЛЯ_БАЗЫ:\s*\[?(.*?)\]?$", ai_response)
                    doctor_name = match.group(1).strip() if match else "Терапевт"

                    # Удаление технической строки
                    clean_response = re.sub(r"ВРАЧ_ДЛЯ_БАЗЫ:.*", "", ai_response).strip()


                    SymptomAnalysis.objects.create(
                        user_query=user_text,
                        ai_result=clean_response,
                        recommended_doctor=doctor_name
                    )
            except Exception as e:
                logger.error(f"GigaChat Error: {e}")
                error_message = "Произошла ошибка при связи с ИИ. Попробуйте позже"
        
        return render(request, self.template_name, {
            "symptoms": user_text,
            "response": clean_response,
            "error": error_message
        })


class HomeView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_card"] = HeroCard.objects.filter(is_active=True).first()
        context["small_cards"] = SmallCard.objects.filter(is_active=True)[:2]
        context["square_cards"] = SquareCard.objects.filter(is_active=True)[:6]
        return context


class SquareCardDetailView(DetailView):
    model = SquareCard
    template_name = "core/square_card_detail.html"
    context_object_name = "card"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self):
        return get_object_or_404(SquareCard, slug=self.kwargs["slug"])


class DoctorsListView(ListView):
    model = Doctor
    template_name = "navbar/doctors_list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        return Doctor.objects.all()


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "navbar/doctor_detail.html"
    context_object_name = "doctor"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Берём доступные слоты для текущего врача
        doctor_slug = self.object.slug
        slots = get_available_slots_queryset(doctor_slug)

        # Группируем слоты по дате
        slots_by_date = {}
        for slot in slots:
            slots_by_date.setdefault(slot.date, []).append(slot)

        # Отзывы только от пациентов завершивших прием
        completed_patients = (
            Schedule.objects.filter(
                doctor=self.object, status="completed", booked_by__isnull=False
            )
            .values_list("booked_by_id", flat=True)
            .distinct()
        )

        reviews = Review.objects.filter(
            doctor=self.object, patient__id__in=completed_patients
        ).select_related("patient")

        # Кладём в контекст
        context["reviews"] = reviews
        context["avg_rating"] = reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        context["review_count"] = reviews.count()
        context["slots_by_date"] = slots_by_date

        return context


class ServicesListView(ListView):
    model = Services
    template_name = "navbar/services_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Services.objects.all()


class PromotionView(ListView):
    model = Promotion
    template_name = "navbar/promotion_list.html"
    context_object_name = "promotion"

    def get_queryset(self):
        return Promotion.objects.all()


class ContactsView(ListView):
    model = Contacts
    template_name = "navbar/contacts.html"
    context_object_name = "contacts"


class TermsOfUseView(TemplateView):
    template_name = "core/legal/terms_of_use.html"


class PrivacyPolicyView(TemplateView):
    template_name = "core/legal/privacy_policy.html"


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "navbar/review_form.html"
    success_url = reverse_lazy("core:doctor_detail")

    def dispatch(self, request, *args, **kwargs):
        self.doctor = get_object_or_404(Doctor, slug=kwargs.get("slug"))
        has_completed = Schedule.objects.filter(
            doctor=self.doctor, booked_by=request.user, status="completed"
        ).exists()
        if not has_completed:
            messages.error(
                request, "Вы можете оставить отзыв только после завершённого приёма"
            )
            return redirect("doctor_detail", slug=self.doctor.slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doctor = self.doctor
        form.instance.patient = self.request.user
        messages.success(self.request, "Отзыв успешно добавлен")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("doctor_detail", kwargs={"slug": self.doctor.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.doctor
        return context
    


