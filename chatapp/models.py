from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
import shortuuid
from django.dispatch import receiver
from chatapp.manager import ThreadManager

GENDER = (
    ('male','Male'),
    ('female','Female'),
)

class CustomUser(AbstractUser):
    email = models.EmailField(max_length = 100, unique = True)
    username = models.CharField(blank = True,null = True,max_length = 30,unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self,*args,**kwargs):
        self.email = self.email.lower()
        return super().save(*args,**kwargs)
    
    def get_profile(self):
        return ProfileModel.objects.get_or_create(user=self)[0]
    
@receiver(post_save,sender = CustomUser)
def save_username_when_user_is_created(sender,instance,created,*args,**kwargs):
    if created:
        email = instance.email
        sliced_email = email.split('@')[0]
        instance.username = sliced_email
        instance.save()

class ProfileModel(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,unique=True,related_name='profile')
    picture = models.ImageField(upload_to='profile_picture',null=True,blank = True)
    friends = models.ManyToManyField(CustomUser,related_name='friends',blank=True)
    bio = models.TextField(blank=True,null=True)
    gender = models.CharField(max_length=6,choices=GENDER,default='none')

class CreateCommunity(models.Model):
    Group_name = models.CharField(max_length=100,unique=True)

    def __str__(self) -> str:
        return self.Group_name
    
class GroupMessage(models.Model):
    group = models.ForeignKey(CreateCommunity,on_delete=models.CASCADE)
    auther = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    body = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class FriendRequest(models.Model):
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='send_request')
    receiver_in = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='receiver_request')
    seen = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f"{self.sender.username} sent {self.receiver_in.username} a friend request "
    

class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Thread(TrackingModel):
    THREAD_TYPE = (
        ('personal', 'Personal'),
        ('group', 'Group')
    )

    name = models.CharField(max_length=50, null=True, blank=True)
    thread_type = models.CharField(max_length=15, choices=THREAD_TYPE, default='personal')
    users = models.ManyToManyField(CustomUser)

    objects = ThreadManager()

    def __str__(self) -> str:
        if self.thread_type == 'personal' and self.users.count() == 2:
            return f'{self.users.first()} and {self.users.last()}'
        return f'{self.name}'

class Message(TrackingModel):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)

    def __str__(self) -> str:
        return f'From <Thread - {self.thread}>'