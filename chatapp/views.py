from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from .models import *
from .form import *
from django.contrib.auth import authenticate, login,logout
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import json
@login_required(login_url='login')
def home(request):
    friend_list = ProfileModel.objects.get(user = request.user)
    friend_list = friend_list.friends.all()
    context = {
        'friendlist':friend_list,
    }
    return render(request, "home.html",context)

def register(request):
    form = RegisterFrom()
    if request.method == 'POST':
        form = RegisterFrom(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email = email , password = password)
            print(user)
            login(request,user)
            messages.success(request,"your are signed in successfully")
            return redirect("home")
    else:
        form = RegisterFrom()

    return render(request,'register.html',{'form':form})

def user_login(request):
    form = LoginForm()   
    if request.method == 'POST':
        form = LoginForm(request.POST)
        email = form.data['email']
        password = form.data['password']
        user = authenticate(request,email = email , password = password)
        if user is not None:
            print(user)
            login(request,user)
            messages.success(request,"your are logged in successfully")
            return redirect('home')
        else:
            form.add_error(None, _('invalid credentials'))
    return render(request,'login.html',{'form':form})


def signout(request):
    logout(request)
    messages.success(request,"you have been logged out")
    return redirect("home")

@login_required(login_url='login')
def UpdateProfile(request,pk):
    user = CustomUser.objects.get(id = pk) 
    profile = ProfileModel.objects.get(user = user)
    
    if request.method == 'POST':  
        user_form = CustomUserForm(request.POST, instance=user)
        profile_form = ProfileModelForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('update-profile', pk=user.id) 
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        user_form = CustomUserForm(instance=user)
        profile_form = ProfileModelForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    } 
    return render(request, 'updateprofile.html', context)



@login_required(login_url='login')
def SearchUsers(request):
    form = SearchForm()
    profile_user = None
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            username = form.data['username']
            users = CustomUser.objects.filter(username=username)
            if users.exists():
                profile_user = users
            else:
                messages.error(request,'user does not exits')
                
    context = {
        'form':form,
        'profile_user':profile_user
    }

    return render(request,'findfriends.html',context)


@login_required(login_url='login')
def send_friend_request(request):
    data = json.loads(request.body)
    user_id = data['id']
    user_value = data['value']
    receiver = CustomUser.objects.get(id=user_id)
    if user_value == 'cancel':
        delete_request = FriendRequest.objects.filter(sender = request.user,receiver_in = receiver )
        delete_request.delete()
    elif user_value == 'add-friend':
        FriendRequest.objects.create(sender = request.user,receiver_in = receiver)

    return JsonResponse({'message': 'send the request'}, safe=False)

# adding and deleting the friend request
@login_required(login_url='login')
def UserProfile(request,pk):
    searching_user = CustomUser.objects.get(pk = pk)
    searching_user_details = ProfileModel.objects.get(user = searching_user) # to show the details of the search user 
    me = ProfileModel.objects.get(user = request.user) # to find the friends in my friend list
    friend_request = FriendRequest.objects.filter(sender = request.user,receiver_in = pk)
    friend_exists = False
    if friend_request:
        friend_exists = True
    context = {
        'myprofiledetail': me,
        'searchuser':searching_user,
        'friend_exists':friend_exists,
        'receiverdetails':searching_user_details,

    }
    return render(request,'profile.html',context)



#conforming the friend request in the notification page
@login_required(login_url='login')  
def adding_friend(request):
    data = json.loads(request.body)
    user_id = data['id']
    user_value = data['value']

    if user_value == 'confirm' and user_id:
        
        sender_user_instance = CustomUser.objects.get(pk = user_id)
        receiver_user_instance = CustomUser.objects.get(pk = request.user.id)

        sender_profile = ProfileModel.objects.get(user = sender_user_instance)
        receiver_profile = ProfileModel.objects.get(user = request.user)

        sender_profile.friends.add(receiver_user_instance)
        receiver_profile.friends.add(sender_user_instance)

        sender_profile.save()
        receiver_profile.save()

        delete_friend_request = FriendRequest.objects.get(sender = user_id,receiver_in = request.user.id)
        delete_friend_request.delete()      

        print('the request is confirmed so add the both are friends in the profile')

    elif user_value == 'cancel':
        delete_friend_request = FriendRequest.objects.get(sender = user_id,receiver_in = request.user.id)
        delete_friend_request.delete()
        print('the request is confirmed so add the both are friends in the profile')

    return JsonResponse({'status': 'success'},safe=False)

def notifications(request):
        friend_requests = FriendRequest.objects.filter(receiver_in =request.user)
        context = {
            'friend_requests': friend_requests
        }
        return render(request, 'notifications.html', context)


@login_required(login_url='login')
def PersonalChat(request,pk):
    Sender = request.user
    Receiver = CustomUser.objects.get(id = pk)
    thread_id = Thread.objects.get_or_create_personal_thread(Sender,Receiver)
    messages = Message.objects.filter(thread=thread_id)
    return render(request,'personalchat.html',{'messages':messages,'sender':Receiver}) 