

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from maills.utils.get_emails import EmailWorker

class MessageConsumer(AsyncWebsocketConsumer):
    EmailWorker: EmailWorker
    async def connect(self):
        await self.accept()
        self.session = self.scope['session']
        self.email = self.session.get('email')
        
        self.email_type = self.session.get('email_type')
        if(self.email and self.email_type):
            await self.start_fetching()


    async def disconnect(self, close_code):
        self.email_worker.stop_fetching()
        await self.close()


    async def start_fetching(self):
        print("start_fetching")
        self.email_worker = EmailWorker(self.email, self.email_type)
        await self.email_worker.fetch_emails(self)