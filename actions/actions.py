# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from langid.langid import LanguageIdentifier, model
from googletrans import Translator

# Instantiate a global translator if desired.
# Alternatively, you can instantiate a new Translator in the helper function.
DEFAULT_TRANSLATOR = Translator()


def translate_text(text: Text, dest: Text, translator: Translator = DEFAULT_TRANSLATOR) -> Text:
    """
    Helper function to translate a given text to the desired destination language.
    If translation fails, the original text is returned.
    """
    try:
        result = translator.translate(text, dest=dest)
        # In case the translator returns a coroutine (async), you could await it if needed.
        return result.text if hasattr(result, "text") else text
    except Exception as e:
        print(f"Translation error for '{text}' to '{dest}': {e}")
        return text


class ActionGreet(Action):
    """Greet the customer and offer main HR options."""
    def name(self) -> Text:
        return "action_greet"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = "Dear Customer, welcome to Tramontina HR assistant. How can I assist you today?"
        buttons = [
            {"title": "PF", "id": "/PF"},
            {"title": "Payroll & Attendance", "id": "/Payroll_Att"},
            {"title": "Reimbursement", "id": "/Reimbursement"},
            {"title": "Language Options", "id": "/Language_Opt"},
            {"title": "Exit", "id": "/goodbye"}
        ]
        # Determine the user language based on the incoming message
        user_lang = 'en'
        lang_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        detected_lang, confidence = lang_identifier.classify(tracker.latest_message.get('text', ''))
        if confidence > 0.5:
            user_lang = detected_lang

        # Translate message and buttons if necessary
        if user_lang != "en":
            message = translate_text(message, dest=user_lang)
            buttons = [
                {"title": translate_text(button["title"], dest=user_lang), "id": button["id"]}
                for button in buttons
            ]
        dispatcher.utter_message(text=message, buttons=buttons)
        return [SlotSet("language", user_lang)]


class ActionLanguageMenu(Action):
    """Provide a menu for the user to select their preferred language."""
    def name(self) -> Text:
        return "action_language"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get("language", "en")
        base_message = "Please select your preferred language:"
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        
        buttons = [
            {"title": "English", "id": "en"},
            {"title": "Malayalam", "id": "ma"},
            {"title": "Hindi", "id": "hi"},
            {"title": "Tamil", "id": "ta"},
            {"title": "Telegu", "id": "te"},
            {"title": "Kannada", "id": "kn"},
            {"title": "Marathi", "id": "mr"},
        ]
        # Translate button titles if necessary
        if language != "en":
            for button in buttons:
                button["title"] = translate_text(button["title"], dest=language)
                
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionPayrollandattMenu(Action):
    """Present Payroll & Attendance options."""
    def name(self) -> Text:
        return "action_payroll"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get("language", "en")
        base_message = "Please select your preferred option:"
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        
        buttons = [
            {"title": "Payroll", "id": "Payroll"},
            {"title": "Attendance", "id": "Attendance"},
        ]
        if language != "en":
            buttons = [
                {"title": translate_text(button["title"], dest=language), "id": button["id"]}
                for button in buttons
            ]
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionThanks(Action):
    """Thank the user and confirm further assistance."""
    def name(self) -> Text:
        return "action_thanks"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract the last couple of user messages for context (if needed)
        reversed_events = list(reversed(tracker.events))
        user_messages = []
        for event in reversed_events:
            if event.get("event") == "user" and len(user_messages) < 2:
                user_messages.append(event.get("text"))
        print("Recent user messages:", user_messages)
        
        dispatcher.utter_message(text="Thanks for your reply. We will connect you soon.")
        return []


class ActionPF(Action):
    """Handle Provident Fund queries."""
    def name(self) -> Text:
        return "action_pf"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get('language', 'en')
        base_message = "Can you tell me what kind of details you need from your PF?"
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        dispatcher.utter_message(text=message)
        return []


class ActionPayroll(Action):
    def name(self) -> Text:
        return "action_pay"
    
    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get('language', 'en')
        translator = Translator()
        # Await the translate call
        translation = translator.translate("Can you tell me what kind of details you need from your payroll?", dest=language)
        message = translation.text
        dispatcher.utter_message(text=message)
        return []


class ActionAttendance(Action):
    """Handle Attendance queries."""
    def name(self) -> Text:
        return "action_attendance"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get('language', 'en')
        base_message = "Can you tell me what is your employee id?"
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        dispatcher.utter_message(text=message)
        return []


class ActionReimbursementMenu(Action):
    """Provide options for Reimbursement queries."""
    def name(self) -> Text:
        return "action_reimbursement_menu"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get("language", "en")
        base_message = "Please select from the following options for your Reimbursement claim:"
        message = translate_text(base_message, dest=language) if language != "en" else base_message

        buttons = [
            {"title": "Travel allowance", "id": "TA"},
            {"title": "Driver's salary", "id": "DS"},
            {"title": "Petrol allowance", "id": "PA"}
        ]
        if language != "en":
            buttons = [
                {"title": translate_text(button["title"], dest=language), "id": button["id"]}
                for button in buttons
            ]
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionTravelAllowance(Action):
    """Provide details about travel allowance claims."""
    def name(self) -> Text:
        return "action_travel_allowance"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get("language", "en")
        base_response = "The amount will be credited to your account."
        response_text = translate_text(base_response, dest=language) if language != "en" else base_response
        dispatcher.utter_message(text=response_text)
        return []


class ActionPetrolAllowance(Action):
    """Handle Petrol Allowance queries."""
    def name(self) -> Text:
        return "action_Petrol_allowance"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language") or "en"
        base_message = "Could you please tell me the distance you traveled?"
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        dispatcher.utter_message(text=message)
        return []


class ActionDriverSalary(Action):
    """Handle Driver Salary queries."""
    def name(self) -> Text:
        return "action_Driver_salary"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.get_slot("language") or "en"
        base_message = "The amount will be credited to the driver account."
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        dispatcher.utter_message(text=message)
        return []


class ActionDefault(Action):
    """Fallback or default action when no other action is triggered."""
    def name(self) -> Text:
        return "action_default"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Please hold on while our staff assist you.")
        return []


class ActionExit(Action):
    """Exit action to end the conversation politely."""
    def name(self) -> Text:
        return "action_goodbye"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language = tracker.slots.get('language', 'en')
        base_message = "Thank you for contacting us. We will be glad to assist you in future as well."
        message = translate_text(base_message, dest=language) if language != "en" else base_message
        dispatcher.utter_message(text=message)
        return []