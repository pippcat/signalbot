# Signalbot

Signalbot is a Python script which can send Signal messages via Email and/or SMS (using www.clockworksms.com API). It's relying on signal-cli (https://github.com/AsamK/signal-cli) to fetch the actual messages. Configuration is done in by renaming config_default.ini to config.ini and modifying it.

## Warning

This script is pretty untested and therefore results may vary. Feel free to try and help me improve it.

## CLI arguments

You may pass the following arguments to signalbot.py to overwrite defaults set in config.ini:

`--mail` override config and send mail

`--nomail` override config and do not send mail

`--sms` override config and send SMS

`--nosms` override config and do not send SMS

`--fetch` override config and fetch new signal messages

`--nofetch` override config and do not fetch new signal messages

`--debug` override config and switch on debug mode

`--nodebug` override config and switch off debug mode

`--emptydb` override config and delete message database after processing

`--noemptydb` override config and keep message database after processing

## ToDos

- check for incoming mails or sms in order to send messages back to group
- add possibility to choose between (multiple) groups and contacts to be forwarded
- check message length and split into multiple sms if necessary


## Changelog
0.5 - fixed unicode fuckup
0.4 - included check for maximum attachment size
0.3 - included contact names
0.2 - now with config.ini
0.1 - first quick and dirty implementation
