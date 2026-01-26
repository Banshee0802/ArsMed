from django.contrib import admin
from .models import (HeroCard, SmallCard, SquareCard, 
                     Doctor, Services, Promotion, 
                     Contacts, Schedule, Review
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
