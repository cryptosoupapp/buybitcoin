# -*- coding: utf-8 -*-
import random
import logging
import requests
import json
import six
from datetime import datetime
from typing import Union, List

from ask_sdk_model import ui
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response, IntentRequest
from ask_sdk_model.interfaces.connections import SendRequestDirective
from ask_sdk_model.interfaces.alexa.presentation.apl import (RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand, AutoPageCommand, HighlightMode)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def http_get(url):
    """Return a response JSON for a GET call from `request`."""
    # type: (str, Dict) -> Dict
    response = requests.get(url)

    if response.status_code < 200 or response.status_code >= 300:
        response.raise_for_status()

    return response.json()

def get_slot_values(filled_slots):
    """Return slot values with additional info."""
    # type: (Dict[str, Slot]) -> Dict[str, Any]
    slot_values = {}
    logger.info("Filled slots: {}".format(filled_slots))

    for key, slot_item in six.iteritems(filled_slots):
        name = slot_item.name

        try:
            status_code = slot_item.resolutions.resolutions_per_authority[0].status.code

            if status_code == StatusCode.ER_SUCCESS_MATCH:
                slot_values[name] = {
                    "synonym": slot_item.value,
                    "resolved": slot_item.resolutions.resolutions_per_authority[0].values[0].value.name,
                    "is_validated": True,
                }
            elif status_code == StatusCode.ER_SUCCESS_NO_MATCH:
                slot_values[name] = {
                    "synonym": slot_item.value,
                    "resolved": slot_item.value,
                    "is_validated": False,
                }
            else:
                pass

        except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
            logger.info("Couldn't resolve status_code for slot item: {}".format(slot_item))
            logger.info(e)
            slot_values[name] = {
                "synonym": slot_item.value,
                "resolved": slot_item.value,
                "is_validated": False,
            }

    return slot_values

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")

        welcomes = ["What a <prosody volume='loud'>great</prosody> day for crypto! How can I help?",
                    "<prosody volume='x-loud'>Hello</prosody>, <prosody volume='loud'>fellow</prosody> cryptopian! How can I assist?",
                    "<prosody volume='x-loud'>Hi</prosody> there! Not a day without crypto, am I right? How can I help?",
                    "Well <prosody volume='loud'>hello</prosody> <prosody volume='loud'>there</prosody>, my sweet little crypto nerd! How can I assist?",
                    "<prosody volume='x-loud'>Greetings</prosody> from planet crypto! How can I help?",
                    "<prosody volume='x-loud'>Bonjour</prosody>, my crypto friend! How can I assist?",
                    "<prosody volume='x-loud'>Howdy</prosody>, my precious <prosody volume='loud'>crypto</prosody> geek! How can I help?",
                    "<prosody volume='x-loud'>Greetings</prosody>, my <prosody volume='loud'>crypto</prosody> comrade! How can I assist?",
                    "Look who it <prosody volume='loud'>is</prosody>, my crypto buddy! How can I help?",
                    "<prosody volume='x-loud'>Cheers</prosody>, my <prosody volume='loud'>crypto</prosody> soul mate! How can I assist?",
                    "<prosody volume='x-loud'>Hello</prosody>, crypto partner! Nice to hear you! How can I help?",
                    "<prosody volume='x-loud'>Hey!</prosody> Your crypto cousin here! How can I assist?",
                    "<prosody volume='x-loud'>Hola</prosody>, my dearest crypto amigo! How can I help?",
                    "<prosody volume='x-loud'>Ciao</prosody>, my beloved <prosody volume='loud'>crypto</prosody> novice! How can I assist?",
                    "<prosody volume='x-loud'>Aloha</prosody>, my cherished <prosody volume='loud'>crypto</prosody> addict! How can I help?",
                    "<prosody volume='x-loud'>Welcome</prosody>, my dear <prosody volume='loud'>crypto</prosody> buddy! How can I assist?",
                    "It's great to hear you, my sweet crypto geek! How can I help?",
                    "So nice to hear you, my lovely <prosody volume='loud'>crypto</prosody> noob! How can I assist?"]

        nice_fallbacks = ["Excuse me, I was checking my portfolio. Can you say it again?",
                          "<say-as interpret-as='interjection'>Damn</say-as>, my <prosody volume='loud'>wallet</prosody> looks so good! Can you repeat?",
                          "Sorry, I didn't get that. I was stacking satoshis. Can you rephrase?",
                          "Sorry, I got a text from Satoshi. Can you say that again?",
                          "Sorry, I was checking my <prosody volume='loud'>crypto</prosody> wallet. Please say that again.",
                          "I beg your pardon, I was checking the price of <prosody volume='loud'>Bit</prosody>coin. Come again?",
                          "Forgive me, I was texting this guy, Nakamoto. Say that again, please!",
                          "I'm sorry, I was buying some coins. Can you repeat?",
                          "Excuse me, Satoshi keeps calling me. Please repeat!",
                          "Oups, you caught me checking my <prosody volume='loud'>crypto</prosody> stack. Say that again, please!"]

        speech = random.choice(welcomes)
        reprompt = random.choice(nice_fallbacks)

        if handler_input.request_envelope.context.system.device.supported_interfaces.alexa_presentation_apl:
            return handler_input.response_builder.speak(speech).ask(reprompt).add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=_load_apl_document("aplbuybitcoin.json"),
                                    datasources={
                                        "bodyTemplate6Data": {
                                            "type": "object",
                                            "objectId": "bt6Sample",
                                            "backgroundImage": {
                                                "sources": [
                                                    {
                                                        "url": "https://yakkie.app/wp-content/uploads/2019/09/bbback.png",
                                                        "size": "small",
                                                        "widthPixels": 0,
                                                        "heightPixels": 0
                                                    },
                                                    {
                                                        "url": "https://yakkie.app/wp-content/uploads/2019/09/bbback.png",
                                                        "size": "large",
                                                        "widthPixels": 0,
                                                        "heightPixels": 0
                                                    }
                                                ]
                                            },
                                            "textContent": {
                                                "primaryText": {
                                                    "type": "PlainText",
                                                    "text": "Hi"
                                                },
                                                "secondaryText": {
                                                    "type": "PlainText",
                                                    "text": ""
                                                }
                                            },
                                            "logoUrl": "https://yakkie.app/wp-content/uploads/2019/09/buybitcoin.png",
                                            "hintText": "Try, \"How many Bitcoin can I buy with 100 dollars?\""
                                        }
                                    }
                                )
                    ).response

        else:
            return handler_input.response_builder.speak(speech).ask(reprompt).set_card(
                ui.StandardCard(
                    title = "Hi",
                    text = "",
                    image = ui.Image(
                        small_image_url = "https://yakkie.app/wp-content/uploads/2019/09/bbcard.png",
                        large_image_url = "https://yakkie.app/wp-content/uploads/2019/09/bbcard.png"
                    ))).response

class InProgressHowMuchIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("HowMuchIsCryptoInFiat")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In InProgressHowMuchIntent")
        current_intent = handler_input.request_envelope.request.intent

        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent = current_intent
            )).response

class HowMuchIsCryptoInFiat(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HowMuchIsCryptoInFiat")(handler_input)

    def handle(self, handler_input):
        logger.info("In HowMuchIsCryptoInFiat")

        price_api_link = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR&api_key=4ca8ca1f2f7499823cde74ea2212edbd64d972f770b8d28708224065f262bf46&e=Coinbase"
        price_api_result = http_get(price_api_link)

        price_usd = list(price_api_result.values())[0]
        price_eur = list(price_api_result.values())[1]

        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = get_slot_values(filled_slots)
        #print(slot_values)

        if slot_values['integer']['resolved'] == None:
                slot_values['integer']['resolved'] = '0'

        elif slot_values['decimal']['resolved'] == None:
            slot_values['decimal']['resolved'] = '0'

        number = float(slot_values['integer']['resolved'] + "." + slot_values['decimal']['resolved'])

        result_usd = number * price_usd
        result_eur = number * price_eur

        if slot_values['fiat']['resolved'] == 'USD':
            speech = "{} {} is worth {} U.S. dollars.".format(number, slot_values['crypto']['resolved'], result_usd)

            if handler_input.request_envelope.context.system.device.supported_interfaces.alexa_presentation_apl:
                return handler_input.response_builder.speak("{} {}".format(speech, get_random_yes_no_question())).ask(get_random_yes_no_question()).add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=_load_apl_document("aplbuybitcoin.json"),
                                    datasources={
                                        "bodyTemplate6Data": {
                                            "type": "object",
                                            "objectId": "bt6Sample",
                                            "backgroundImage": {
                                                "sources": [
                                                    {
                                                        "url": "https://yakkie.app/wp-content/uploads/2019/09/bbback.png",
                                                        "size": "small",
                                                        "widthPixels": 0,
                                                        "heightPixels": 0
                                                    },
                                                    {
                                                        "url": "https://yakkie.app/wp-content/uploads/2019/09/bbback.png",
                                                        "size": "large",
                                                        "widthPixels": 0,
                                                        "heightPixels": 0
                                                    }
                                                ]
                                            },
                                            "textContent": {
                                                "primaryText": {
                                                    "type": "PlainText",
                                                    "text": str(result_usd) + " USD"
                                                },
                                                "secondaryText": {
                                                    "type": "PlainText",
                                                    "text": str(number) + " BTC"
                                                }
                                            },
                                            "logoUrl": "https://yakkie.app/wp-content/uploads/2019/08/logo-noB.png",
                                            "hintText": "Try, \"How many Bitcoin can I buy with 100 dollars?\""
                                        }
                                    }
                                )
                    ).response
            else:
                return handler_input.response_builder.speak("{} {}".format(speech, get_random_yes_no_question())).ask(get_random_yes_no_question()).set_card(
                ui.StandardCard(
                    title = str(result_usd) + " USD",
                    text = str(number) + " BTC",
                    image = ui.Image(
                        small_image_url = "https://yakkie.app/wp-content/uploads/2019/09/bbcard.png",
                        large_image_url = "https://yakkie.app/wp-content/uploads/2019/09/bbcard.png"
                    ))).response

        elif slot_values['fiat']['resolved'] == 'EUR':
            speech = "{} {} is worth {} Euros.".format(number, slot_values['crypto']['resolved'], result_eur)

            if handler_input.request_envelope.context.system.device.supported_interfaces.alexa_presentation_apl:
                return handler_input.response_builder.speak("{} {}".format(speech, get_random_yes_no_question())).ask(get_random_yes_no_question()).add_directive(
                                RenderDocumentDirective(
                                    token="pagerToken",
                                    document=_load_apl_document("aplbuybitcoin.json"),
                                    datasources={
                                        "bodyTemplate6Data": {
                                            "type": "object",
                                            "objectId": "bt6Sample",
                                            "backgroundImage": {
                                                "sources": [
                                                    {
                                                        "url": "https://yakkie.app/wp-content/uploads/2019/09/bbback.png",
                                                        "size": "small",
                                                        "widthPixels": 0,
                                                        "heightPixels": 0
                                                    },
                                                    {
                                                        "url": "https://yakkie.app/wp-content/uploads/2019/09/bbback.png",
                                                        "size": "large",
                                                        "widthPixels": 0,
                                                        "heightPixels": 0
                                                    }
                                                ]
                                            },
                                            "textContent": {
                                                "primaryText": {
                                                    "type": "PlainText",
                                                    "text": str(result_eur) + " EUR"
                                                },
                                                "secondaryText": {
                                                    "type": "PlainText",
                                                    "text": str(number) + " BTC"
                                                }
                                            },
                                            "logoUrl": "https://yakkie.app/wp-content/uploads/2019/08/logo-noB.png",
                                            "hintText": "Try, \"How many Bitcoin can I buy with 100 euro?\""
                                        }
                                    }
                                )
                    ).response
            else:
                return handler_input.response_builder.speak("{} {}".format(speech, get_random_yes_no_question())).ask(get_random_yes_no_question()).set_card(
                ui.StandardCard(
                    title = str(result_eur) + " EUR",
                    text = str(number) + " BTC",
                    image = ui.Image(
                        small_image_url = "https://yakkie.app/wp-content/uploads/2019/09/bbcard.png",
                        large_image_url = "https://yakkie.app/wp-content/uploads/2019/09/bbcard.png"
                    ))).response


class InProgressHowManyIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("HowManyIsCryptoInFiat")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In InProgressHowMuchIntent")
        current_intent = handler_input.request_envelope.request.intent

        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent = current_intent
            )).response

class HowManyCryptoCanIBuy(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HowManyCryptoCanIBuy")(handler_input)

    def handle(self, handler_input):
        logger.info("In HowManyCryptoCanIBuy")

        price_api_link = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR&api_key=4ca8ca1f2f7499823cde74ea2212edbd64d972f770b8d28708224065f262bf46&e=Coinbase"
        price_api_result = http_get(price_api_link)

        price_usd = list(price_api_result.values())[0]
        price_eur = list(price_api_result.values())[1]

        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = get_slot_values(filled_slots)
        #print(slot_values)

class RepeatHandler(AbstractRequestHandler):
    """Repeat last fact/legend."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In RepeatHandler")

        return handler_input.response_builder.speak("{}".format(handler_input.attributes_manager.session_attributes["lastSpeech"])).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        speech = "Well, my little crypto friend, you basically hav two options. You can ask me, for instance, 'How much is 2.5 Bitcoin in U.S. dollars?', or, something like 'How many Bitcoin can I buy for 100 Euro?'. So, how can I help you?"

        handler_input.attributes_manager.session_attributes["lastSpeech"] = speech

        return handler_input.response_builder.speak(speech).ask(speech).response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        nice_fallbacks = ["Excuse me, I was checking my portfolio. Can you say it again?",
                          "<say-as interpret-as='interjection'>Damn</say-as>, my <prosody volume='loud'>wallet</prosody>coin looks so good! Can you repeat?",
                          "Sorry, I didn't get that. I was stacking satoshis. Can you rephrase?",
                          "Sorry, I got a text from Satoshi. Can you say that again?",
                          "Sorry, I was checking my <prosody volume='loud'>Bit</prosody>coin wallet. Please say that again.",
                          "I beg your pardon, I was checking the price of <prosody volume='loud'>Bit</prosody>coin. Come again?",
                          "Forgive me, I was texting this guy, Nakamoto. Say that again, please!",
                          "I'm sorry, I was buying some coins. Can you repeat?",
                          "Excuse me, Satoshi keeps calling me. Please repeat!",
                          "<prosody volume='loud'>Oups</prosody>, you caught me checking my <prosody volume='loud'>Bit</prosody>coin stack. Say that again, please!"]

        speech = random.choice(nice_fallbacks)

        return handler_input.response_builder.speak(speech).ask(speech).response

class SessionEndedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("SessionEndedRequest")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.CancelIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedHandler")

        return handler_input.response_builder.speak(get_random_goodbye()).set_should_end_session(True).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        sorrys = ["Sorry, I can't understand the command. Please try again!",
                  "I'm not sure I understand your wish. Say it again! I'm all ears.",
                  "I didn't catch that. Can you repeat, please?"]

        speech = random.choice(sorrys)

        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(handler_input.request_envelope))

class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


sb = StandardSkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(InProgressHowMuchIntent())
sb.add_request_handler(InProgressHowManyIntent())
sb.add_request_handler(HowMuchIsCryptoInFiat())
sb.add_request_handler(HowManyCryptoCanIBuy())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedHandler())
sb.add_request_handler(RepeatHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()

#End of program
