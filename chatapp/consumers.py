import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import SyncConsumer
from .models import *

class PersonalChatConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.Sender = self.scope['user']
        self.Receiver_id = self.scope['url_route']['kwargs']['id']
        Receiver = CustomUser.objects.get(id = self.Receiver_id)
        self.thred_obj = Thread.objects.get_or_create_personal_thread(self.Sender,Receiver)

        self.room_name = f'personal_thread_{self.thred_obj.id}'
        async_to_sync(self.channel_layer.group_add)(self.room_name,self.channel_name)

        self.send({
                "type": "websocket.accept"
            })
        
        print('your connected')

    def websocket_receive(self, event):
        print(event)
        msg = json.dumps({
            'text': event.get('text'),
            'username':self.scope['user'].username
        })
        async_to_sync(self.channel_layer.group_send)(self.room_name,{'type':'websocket.message','text':msg})
        
        self.store_message(event.get('text'))

    def websocket_message(self,event):
        self.send({
            'type':'websocket.send',
            'text': event.get('text')
        })

    def websocket_disconnect(self,event):
        async_to_sync(self.channel_layer.group_discard)(self.room_name,self.channel_name)
        print('disconnected')

    def store_message(self,text):
        Message.objects.create(thread = self.thred_obj,sender = self.scope['user'],text = text)


class GroupChatCunsumer(SyncConsumer):

    def websocket_connect(self):
        self.send({
                "type": "websocket.accept"
            })
        print(' websocket connected')
    
    def websocket_reveive(self,event):
        print(event)

    def websocket_disconnect(self,event):
        print('wesocket is disconnected')


class NotificationsCunsumer(SyncConsumer):
    def websocket_connect(self):
        self.send({
            'type':'websocket.accept'
        })
        print('wesocket is connected')

    def websocket_receive(self,event):
        FriendRequest.objects.filter(receiver_in = self.scope['user'])
        print(event)

    def websocket_disconnect(self,event):
        print('disconnected')

class friendRequest(SyncConsumer):
    def websocket_connect(self):
        self.send({
            'type':'websocket.accept'
        })
        print('websocket is connected')

    def websocket_receive(self,event):
        print(event)

    def websocket_disconnected(self,event):
        print('disconnected')