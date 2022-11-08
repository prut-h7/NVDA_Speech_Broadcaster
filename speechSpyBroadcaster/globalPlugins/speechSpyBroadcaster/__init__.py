import os
from functools import wraps
# from enum import Enum, unique, auto, IntEnum
import addonHandler
import globalPluginHandler
import globalPlugins
import globalVars
import ui
import gui
import config
import speech
from speech.types import SpeechSequence, Optional
from speech.priorities import Spri
from scriptHandler import script
from logHandler import log

from .configUI import SpeechLoggerSettings, getConf
from .immutableKeyObj import ImmutableKeyObj
import socket

addonHandler.initTranslation()


# @unique
# class Origin(Enum):
#     """Enum to tell our methods where a speech sequence came from."""
#     LOCAL = auto()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def __init__(self):
        super().__init__()
        self.flags = ImmutableKeyObj(
            log_broadcast=False,
            localActive=True
        )
        self.utteranceSeparator = "  "
        self.UDP_socket = ImmutableKeyObj(group=None, port=None, ttl=None)

        if not globalVars.appArgs.secure:
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SpeechLoggerSettings)

        self.applyUserConfig()
        self.UDP_object = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # For all packets sent, after 2 hops on the network the packet will not
        # be re-sent/broadcast
        # IP_MULTICAST_TTL is kept 2 by default; The user can update this in the NVDA settings if needed.
        self.UDP_object.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        old_speak = speech.speech.speak

        @wraps(speech.speech.speak)
        def new_speak(
                sequence: SpeechSequence,
                symbolLevel: Optional[int] = None,
                priority: Spri = Spri.NORMAL
        ):
            self.captureSpeech(sequence)
            return old_speak(sequence, symbolLevel, priority)

        speech.speech.speak = new_speak

    def terminate(self):
        # Remove the NVDA settings panel
        if not globalVars.appArgs.secure:
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SpeechLoggerSettings)

    def applyUserConfigIfNeeded(self):
        """If the user has changed any part of the configuration, reset our internals accordingly."""
        if SpeechLoggerSettings.hasConfigChanges:
            self.applyUserConfig()
            SpeechLoggerSettings.hasConfigChanges = False

    def applyUserConfig(self):

        if getConf("port") == "" or getConf("group") == "" or getConf("ttl") == "":
            self.flags.log_broadcast = False
            self.UDP_socket.group = None
            self.UDP_socket.port = None
            self.UDP_socket.ttl = None
        else:
            self.flags.log_broadcast = True
            self.UDP_socket.group = getConf("group")
            self.UDP_socket.port = int(getConf("port"))
            self.UDP_socket.ttl = int(getConf("ttl"))
            try:
                # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                #     pass
                self.UDP_object.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.UDP_socket.ttl)

            except Exception as e:
                log.error(f"Couldn't establish UDP connection. {e}")
                self.flags.log_broadcast = False
                self.UDP_socket.group = None
                self.UDP_socket.port = None
                self.UDP_socket.ttl = None

        unescapedCustomSeparator = getConf("customSeparator").encode().decode("unicode_escape")
        separators = {
            "2spc": "  ",
            "nl": "\n",
            "comma": ", ",
            "__": "__",
            "custom": unescapedCustomSeparator
        }
        try:
            self.utteranceSeparator = separators[getConf("separator")]
        except KeyError:
            log.error(
                f'Value "{getConf("separator")}", found in NVDA config, is '
                'not a known separator. Using default of two spaces.'
            )
            self.utteranceSeparator = separators["2spc"]  # Use default

    def captureSpeech(self, sequence: SpeechSequence):
        ''' Receives the Speech text and broacasts this on a particular address'''
        self.applyUserConfigIfNeeded()
        group = None
        port = None
        #ttl = None
        if self.flags.localActive:
            group = self.UDP_socket.group
            port = self.UDP_socket.port
            #ttl = self.UDP_socket.ttl
        if [group, port] is not None:
            self.logBroadcaster(sequence, group, port) #, ttl)

    @script(
        category="Tools",
        # Translators: the description of an item in the input gestures tools category
        description=_("Toggles logging of local speech"),
        gesture="kb:NVDA+Alt+B"
    )
    def script_toggleLocalSpeechLogging(self, gesture):
        """Toggles whether we are actively logging local speech."""
        if self.flags.localActive:  # Currently logging, stop
            self.flags.localActive = False
            ui.message(_("Stopped logging local speech."))
        else:
            if self.flags.log_broadcast:
                self.flags.localActive = True
                ui.message(_("Started logging local speech."))
            else:
                ui.message(_("Local speech logging has been disabled by an error or your NVDA configuration."))

    def logBroadcaster(self, sequence: SpeechSequence, group: str, port: int):

        try:
            spy_speech = self.utteranceSeparator.join(
                toSpeak for toSpeak in sequence if isinstance(toSpeak, str))
            #self.UDP_object.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            self.UDP_object.sendto(bytes(spy_speech, 'utf-8'), (group, port))
        except Exception as e:
            log.error(f"Couldn't send data over UDP Port. {e}")
