### NVDA Speech Logger add-on

Author: Pruthivi Raj

An [NVDA](https://nvaccess.org/) add-on to broadcast speech over UDP.
It can broadcast speech generated on the local machine via UDP.
The default UDP Group is 224.1.1.1 with Port - 5004. The TTL value is 2 by default.

### Configuration

To configure this add-on, open the NVDA menu, go to Preferences, then Settings, then Speech Broadcaster.

Note: the add-on can only be configured while in the Normal Configuration profile of NVDA. The add-on is not profile-aware.

The following settings are available:
* The UDP Group. The UDP Group specifies the address where to connect the UDP Receiver. The default value is kept as 224.1.1.1
* The UDP Port. The UDP Port specifies the port where to connect the UDP Receiver. The default value is kept as 5004
* TTL Value. The TTL Value specifies the number of hops in the network. The default value is kept as 2.
* Separator. This combobox lets you choose one of the available utterance separators. See below for more information.
* Custom separator. This field lets you enter a custom utterance separator (see below), which is used if "custom" is chosen in the combobox.

#### Utterance separator

When NVDA speaks something such as "`recycle bin  1 of 55`" while it's reading your desktop, this is considered two separate utterances. The first one is the item name ("`Recycle bin`", in this example), and the second is the object position information ("`1 of 55`", in this example).

Depending on what you are reading, and how you have NVDA configured, there can be several separate utterances that happen during a single speech sequence.

In the normal NVDA log at debug level, each individual utterance is separated with two spaces, as it is written in the example above.

Speech Logger allows you to separate utterances in the same way NVDA does (with two spaces), or by one of a few reasonable alternatives (a newline, a comma and a space, two underscores), or by a custom sequence of your own devising.

If, for example, you wanted your utterance separator to be two dollar signs (`$$`), you would set the combobox to "custom", and enter "`$$`" (without the quotes), in the custom separator field. If you wanted it to be a tab, you could enter "`\t`".

### Starting and stopping broadcasting

This add-on has one gesture set by default. You can change them in the NVDA Input Gestures Tools category.
Look for "Toggles broadcast of local speech".
* NVDA+Alt+B: start/stop broadcast of local speech.
