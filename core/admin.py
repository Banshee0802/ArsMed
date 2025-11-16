from django.contrib import admin
from .models import (HeroCard, SmallCard, SquareCard, 
                     Doctor, Services
                     )

admin.site.register(HeroCard)
admin.site.register(SmallCard)
admin.site.register(SquareCard)
admin.site.register(Doctor)
admin.site.register(Services)
