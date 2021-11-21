from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from user import models
from item.models import ModelCart, ModelOrder, Address, \
                        ItemWithQuantity, ItemAdditive, SaveOrderActions, ScoreActions, Report, \
                        ItemImages, PaymentItem


class UserAdmin(BaseUserAdmin):

    list_display = 'login', 'is_staff'
    ordering = 'login',
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        (_('Personal info'), {'fields': ('name', 'phone', 'type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),

        (_('Important dates'), {'fields': ('last_login', )})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'password1', 'password2')
        }),
    )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.RegularAccount)
admin.site.register(models.Store)
admin.site.register(ModelCart)
admin.site.register(ModelOrder)
admin.site.register(Address)
admin.site.register(ItemWithQuantity)
admin.site.register(models.Rating)
admin.site.register(models.RatingStar)
admin.site.register(SaveOrderActions)
admin.site.register(ScoreActions)
admin.site.register(Report)
admin.site.register(PaymentItem)
admin.site.register(ItemAdditive)
admin.site.register(ItemImages)