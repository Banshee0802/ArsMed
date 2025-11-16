from django.contrib import admin
from .models import (HeroCard, SmallCard, SquareCard, 
                     Doctor, Services, Promotion
                     )

admin.site.register(HeroCard)
admin.site.register(SmallCard)
admin.site.register(SquareCard)
admin.site.register(Doctor)
admin.site.register(Services)
admin.site.register(Promotion)
