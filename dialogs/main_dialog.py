# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import CardFactory, MessageFactory
from botbuilder.dialogs import ConfirmPrompt, DialogSet, DialogTurnStatus, WaterfallDialog
from botbuilder.dialogs.prompts import OAuthPrompt, OAuthPromptSettings

from .logout_dialog import LogoutDialog

from helpers.activity_helper import create_activity_reply

CONFIRM_PROMPT = 'ConfirmPrompt'
MAIN_DIALOG = 'MainDialog'
MAIN_WATERFALL_DIALOG = 'MainWaterfallDialog'
OAUTH_PROMPT = 'OAuthPrompt'

class MainDialog(LogoutDialog):
    def __init__(self, connection_name: str):
        super().__init__(MAIN_DIALOG, connection_name)

        # Define the main dialog and its related components.
        self.add_dialog(OAuthPrompt(OAuthPrompt.__name__,OAuthPromptSettings(
                connection_name= connection_name,
                text= "Please Sign In",
                title= "Sign In",
                timeout= 300000, # User has 5 minutes to login (1000 * 60 * 5)
            )))
        
        #self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.add_dialog(WaterfallDialog(MAIN_WATERFALL_DIALOG, [
            self.prompt_step,
            self.login_step,
            self.display_token_phase1,
            self.display_token_phase2,
        ]))

        # The initial child Dialog to run.
        self.initial_dialog_id = MAIN_WATERFALL_DIALOG

    async def prompt_step(self, step_context):
        return await step_context.begin_dialog(OAUTH_PROMPT)

    async def login_step(self, step_context):
        # Get the token from the previous step. Note that we could also have gotten the
        # token directly from the prompt itself. There is an example of this in the next method.
        token_response = step_context.result
        if (token_response) :
            await step_context.context.send_activity('You are now logged in.')
            return await step_context.next(1)
            #return await step_context.prompt(CONFIRM_PROMPT, 'Would you like to view your token?')
        
        await step_context.context.send_activity('Login was not successful please try again.')
        return await step_context.end_dialog()
    

    async def display_token_phase1(self, step_context) :
        await step_context.context.send_activity('Thank you.')

        result = step_context.result
        if (result) :
            # Call the prompt again because we need the token. The reasons for this are:
            # 1. If the user is already logged in we do not need to store the token locally in the bot and worry
            # about refreshing it. We can always just call the prompt again to get the token.
            # 2. We never know how long it will take a user to respond. By the time the
            # user responds the token may have expired. The user would then be prompted to login again.
            #
            # There is no reason to store the token locally in the bot because we can always just call
            # the OAuth prompt to get the token or get a new token if needed.
            return await step_context.begin_dialog(OAUTH_PROMPT)
        
        return await step_context.end_dialog()
    

    async def display_token_phase2(self, step_context) :
        token_response = step_context.result
        if (token_response) :
            await step_context.context.send_activity(f'Here is your token: {token_response.token} ')
        
        return await step_context.end_dialog()
