import wx

import addonHandler
import config
import ui
import globalVars
import gui
from gui.settingsDialogs import PANEL_DESCRIPTION_WIDTH
from logHandler import log

addonHandler.initTranslation()

#: speechLogger Add-on config database
config.conf.spec["speechLogger"] = {
    "group": "string(default='224.1.1.1')",
    "port": "string(default='5004')",
    "ttl": "string(default='2')",
    "separator": "string(default='2spc')",
    "customSeparator": "string(default='')"
}


def getConf(item: str):
    """Accessor to return NVDA config items in a safe way."""
    return config.conf['speechLogger'][item]


def setConf(key: str, value):
    """Complement of getConf. Sets NVDA config items in a safe way."""
    config.conf['speechLogger'][key] = value
    return value


class SpeechLoggerSettings(gui.settingsDialogs.SettingsPanel):
    """NVDA configuration panel based configurator  for SpeechSpyBroadcaster."""

    #: Class variable to track whether the configuration has been changed in the panel, thus causing the
    #: add-on to refresh its idea of the configuration.
    hasConfigChanges = True

    # Translators: This is the label for the Speech Logger settings category in NVDA Settings dialog.
    title = _("Speech Broadcaster")

    # Translators: the primary introductory text for the settings dialog
    panelDescription_normalProfile = _(
        "Enter the Group and Port number to Broadcast the NVDA speech. "
        "The default TTL Value is 2,change that if needed.\n"
        "You can also alter the string used to separate multiple"
        " utterances from the same speech sequence."
    )
    # Translators: the alternative introductory text for the settings dialog
    panelDescription_otherProfile = _(
        "The Speech Logger add-on can only be configured from the Normal Configuration profile.\n"
        "Please close this dialog, set your config profile to normal, and try again."
    )

    availableSeparators = (
        # Translators: a separator option in the separators combobox
        ("2spc", _("Two spaces (NVDA log style)")),
        # Translators: a separator option in the separators combobox
        ("nl", _("Newline")),
        # Translators: a separator option in the separators combobox
        ("comma", _("A comma and space")),
        # Translators: a separator option in the separators combobox
        ("__", _("Two underscores")),
        # Translators: a separator option in the separators combobox
        ("custom", _("Custom"))
    )

    def makeSettings(self, settingsSizer):
        """Creates a settings panel.
        If an NVDA configuration profile other than "normal" is running, a panel with
        no options and a notification to the user is created.
        """

        # Disable if in secure mode.
        # Can't use blockAction.when, because of compatibility with older versions.
        if globalVars.appArgs.secure:
            return

        if config.conf.profiles[-1].name is None and len(config.conf.profiles) == 1:
            SpeechLoggerSettings.panelDescription = self.panelDescription_normalProfile
        else:
            SpeechLoggerSettings.panelDescription = self.panelDescription_otherProfile

        helper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        introItem = helper.addItem(wx.StaticText(self, label=self.panelDescription))
        introItem.Wrap(self.scaleSize(PANEL_DESCRIPTION_WIDTH))

        if config.conf.profiles[-1].name is not None or len(config.conf.profiles) != 1:
            return

        # Network Group Sizer
        netgroupSizer = wx.StaticBoxSizer(
            wx.VERTICAL, self,
            # Translators: label of the log files location grouping.
            label=_("Network &Parameters: ")
        )
        netGroupHelper = helper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=netgroupSizer))
        netGroupBox = netgroupSizer.GetStaticBox()

        self.udp_group = netGroupHelper.addLabeledControl(
            # Translators: label of the UDP Group Number.
            _("UDP Group Number: "), wx.TextCtrl
        )
        self.udp_group.SetValue(getConf("group"))

        self.udp_port = netGroupHelper.addLabeledControl(
            # Translators: label of the UDP Port Number.
            _("UDP Port Number(Should be integers): "), wx.TextCtrl
        )
        self.udp_port.SetValue(getConf("port"))

        self.udp_ttl = netGroupHelper.addLabeledControl(
            # Translators: label of the TTL Number.
            _("TTL Value(Default=2): "), wx.TextCtrl
        )
        self.udp_ttl.SetValue(getConf("ttl"))

        # Grouping for separator options
        sepGroupSizer = wx.StaticBoxSizer(
            wx.VERTICAL, self,
            # Translators: label of the separator options grouping.
            label=_("&Separator Options")
        )
        sepGroupHelper = helper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=sepGroupSizer))
        sepGroupBox = sepGroupSizer.GetStaticBox()

        # Translators: this is the label for a combobox providing possible separator values
        separatorComboLabel = _("Utterance separator")
        separatorDisplayChoices = [name for setting, name in self.availableSeparators]
        self.separatorChoiceControl = sepGroupHelper.addLabeledControl(
            separatorComboLabel, wx.Choice, choices=separatorDisplayChoices
        )
        # Iterate the combobox choices, and pick the one listed in config
        for index, (setting, name) in enumerate(self.availableSeparators):
            if setting == getConf("separator"):
                self.separatorChoiceControl.SetSelection(index)
                break
        else:  # Unrecognized choice saved in configuration
            log.debugWarning(
                "Could not set separator combobox to the config derived option of"
                f' "{getConf("separator")}". Using default.'
            )
            self.separatorChoiceControl.SetSelection(0)  # Use default

        self.customSeparatorControl = sepGroupHelper.addLabeledControl(
            # Translators: the label for a text field requesting an optional custom separator string
            _(r"Custom utterance separator (can use escapes like \t): "), wx.TextCtrl
        )
        self.customSeparatorControl.SetValue(getConf("customSeparator"))

    def onSave(self):
        """Save the settings to the Normal Configuration."""
        if config.conf.profiles[-1].name is None and len(config.conf.profiles) == 1:
            setConf("group", self.udp_group.Value)
            setConf("port", self.udp_port.Value)
            setConf("ttl", self.udp_ttl.Value)

            sepText = self.availableSeparators[self.separatorChoiceControl.Selection][0]
            setConf("separator", sepText)
            setConf("customSeparator", self.customSeparatorControl.Value)

    def postSave(self):
        """After saving settings, set a flag to cause a config re-read by the add-on."""
        if config.conf.profiles[-1].name is None and len(config.conf.profiles) == 1:
            SpeechLoggerSettings.hasConfigChanges = True
