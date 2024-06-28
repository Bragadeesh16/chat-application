from django.contrib import admin
from .models import *

class ProfileModelInline(admin.StackedInline):
    model = ProfileModel
    can_delete = False 
    verbose_name_plural = 'Profile'
class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileModelInline,)
    list_display = ('email', 'username', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(CustomUser, UserAdmin)
admin.site.register(CreateCommunity)
admin.site.register(GroupMessage)
admin.site.register(FriendRequest)
admin.site.register(Message)
admin.site.register(Thread)