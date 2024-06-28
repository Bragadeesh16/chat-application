from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login",views.user_login,name='login'),
    path("register",views.register,name='register'),
    path("logout",views.signout,name='logout'),
    path('search-user',views.SearchUsers,name='search_user'),
    path('user-profile/<int:pk>',views.UserProfile,name='user-profile'),
    path('update-profile/<int:pk>',views.UpdateProfile,name='update-profile'),
    path('send-request',views.send_friend_request,name='send-request'),
    path('notification',views.notifications,name='notifications'),
    path('adding_friend',views.adding_friend,name='adding-friend'),
    path('personal-chat/<int:pk>',views.PersonalChat,name='personal-chat'),
]