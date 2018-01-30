# Signalbot

Signalbot is a Python script which can send Signal messages via Email and/or SMS (using www.clockworksms.com API). It's relying on signal-cli (https://github.com/AsamK/signal-cli) to fetch the actual messages. Configuration is done in by renaming config_default.ini to config.ini and modifying it.

## Response branch

Email recipients should be able to answer to the signalbot in order for him to pipe the answer back to the group. It's kind of working but still needs some love.

## Warning

This script is only tested on a Raspberry Pi 2 running Raspbian Jessie and Python 2.7.9. Your results may vary. Feel free to try and help me improve it.

## CLI arguments

You may pass the following arguments to signalbot.py to overwrite defaults set in config.ini:

- `--mail` override config and send mail
- `--notmail` override config and do not send mail
- `--sms` override config and send SMS
- `--notsms` override config and do not send SMS
- `--fetch` override config and fetch new signal messages
- `--notfetch` override config and do not fetch new signal messages
- `--getmail` override config and send email responses to group
- `--notgetmail` override config and do not send email responses to group
- `--debug` override config and switch on debug mode
- `--notdebug` override config and switch off debug mode
- `--emptydb` override config and delete message database after processing
- `--notemptydb` override config and keep message database after processing

## Known bugs

- SMS module doesn't check for length of messages

## ToDos

- check for incoming mails or sms in order for recipients to be able to send messages back to group
- add possibility to choose between (multiple) groups and contacts to be forwarded to different recipients
- check message length and split into multiple sms if necessary

## Changelog

- 0.5.2 - code clean up
- 0.5.1 - added timestamp to mail header
- 0.5   - fixed unicode fuckup
- 0.4   - included check for maximum attachment size
- 0.3   - included contact names
- 0.2   - now with config.ini
- 0.1   - first quick and dirty implementation
