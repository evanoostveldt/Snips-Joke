#!/usr/bin/env python3.7

import requests
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes

# imported to get type check and IDE completion
from hermes_python.ontology.dialogue.intent import IntentMessage

CONFIG_INI = "config.ini"

# if this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
#
# hint: MQTT server is always running on the master device
MQTT_IP_ADDR: str = "localhost"
MQTT_PORT: int = 1883
MQTT_ADDR: str = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))


class Joke(object):
    """class used to wrap action code with mqtt connection
       please change the name referring to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except Exception:
            self.config = None

        # start listening to MQTT
        self.start_blocking()

    @staticmethod
    def askJoke_callback(hermes: Hermes,
                          intent_message: IntentMessage):

        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        good_category = requests.get("https://api.chucknorris.io/jokes/categories").json();

        category = None
        if intent_message.slots.category:
            category = intent_message.slots.category.first().value
            # check if the category is valide
            if category.encode("utf-8") not in good_category:
                category = None

        if category is None:
            joke_msg = str(requests.get("https://api.chucknorris.io/jokes/random")\
                                                                   .json().get("value"))
        else:
            joke_msg = str(requests.get("https://api.chucknorris.io/jokes/random?category={}".format(category))\
                                                                  .json().get("value"))

        new_people =  self.config.get("secret").get("protagonist")
        if new_people is not None and new_people is not "":
            joke_msg = joke_msg.replace('Chuck Norris',new_people)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, joke_msg, "Joke_APP")

    # register callback function to its intent and start listen to MQTT bus
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intent('intent_1', self.askJoke_callback)\
            .loop_forever()


if __name__ == "__main__":
    Joke()
