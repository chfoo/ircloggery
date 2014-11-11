ircloggery
==========

Scripts to import xchat2/bip logs into mIRC logs for ircLogger.

Supports combining logs from multiple sources.

Requires Python 3.

Usage::

    python3 ircloggery source1/blahNet-#blahChan.log \
        source2/blahNet-#blahChan.log \
        output_directory/

Note: Mixing different types of logs have adverse effects such as duplicated events or problems with timezones.
