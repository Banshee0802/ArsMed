from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import HeroCard, SmallCard, SquareCard


class HomeView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_card'] = HeroCard.objects.filter(is_active=True).first()
        context['small_cards'] = SmallCard.objects.filter(is_active=True)[:2]
        context['square_cards'] = SquareCard.objects.filter(is_active=True)[:6]
        return context
        

class SquareCardDetailView(DetailView):
    model = SquareCard
    template_name = "core/square_card_detail.html"
    context_object_name = "card"

    def get_object(self):
        return get_object_or_404(SquareCard, slug=self.kwargs['slug'])