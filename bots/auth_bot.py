# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from helpers.dialog_helper import DialogHelper
from .dialog_bot import DialogBot

class AuthBot(DialogBot):
    def __init__(self, conversation_state, user_state, dialog):
        super().__init__(conversation_state, user_state, dialog)

    async def on_members_added_activity(self, members_added, turn_context):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity('Welcome to AuthenticationBot. Type anything to get logged in. Type \'logout\' to sign-out.')

    async def on_token_response_event(self, context):
        await DialogHelper.run_dialog(self.dialog, context, self.dialog_state)
