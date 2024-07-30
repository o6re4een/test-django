

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from maills.utils.get_emails import EmailWorker

class MessageConsumer(AsyncWebsocketConsumer):
    email_worker: EmailWorker

    async def connect(self):
        await self.accept()
        # self.session = self.scope['session']
        # self.email = self.session.get('email')
        # self.email_type = self.session.get('email_type')
        
        # if self.email and self.email_type:
        #     await self.start_fetching()

    async def disconnect(self, close_code):
        # Ensure email_worker is stopped
        if hasattr(self, 'email_worker'):
            print("stop_fetching")
            self.email_worker.stop_fetching()

        await self.close()

    async def start_fetching(self):
        print("start_fetching")
        # Initialize and start fetching emails
        self.email_worker = EmailWorker(self.email, self.email_type)
        await self.email_worker.fetch_emails(self)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('type')
        print(data)
        
        if action == 'fetch_emails':
            # Stop current fetching
            if hasattr(self, 'email_worker'):
                print("stop_fetching")
                self.email_worker.stop_fetching()

            # Get new email details from session
            self.email = data.get("email")
            self.email_type = data.get("email_type")

            if self.email and self.email_type:
              
                await self.start_fetching()