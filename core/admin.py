from django.contrib import admin
from .models import (HeroCard, SmallCard, SquareCard, 
                     Doctor, Services, Promotion, 
                     Contacts, Schedule, Review,
                     SymptomAnalysis
                     )

admin.site.register(HeroCard)
admin.site.register(SmallCard)
admin.site.register(SquareCard)
admin.site.register(Doctor)
admin.site.register(Services)
admin.site.register(Promotion)
admin.site.register(Contacts)
admin.site.register(Schedule)
admin.site.register(Review)

@admin.register(SymptomAnalysis)
class SymptomAnalysisAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user_query_short", "recommended_doctor")
    list_filter = ("created_at", "recommended_doctor")
    readonly_fields = ("created_at", "user_query", "ai_result")

    def user_query_short(self, obj):
        return obj.user_query[:50] + "..."
    user_query_short.short_description = "Жалоба"

