#Flashlight
##Requirements

Tornado >= 3.2.1

##Install and usage

Installation and first run:

    $ git clone https://github.com/skint/samples.git
    $ cd samples
    $ pip install flashlight
    $ flashlight
    Starting Engine with stream.read_until_close()
    Listening on http://0.0.0.0:8888
    ^C
    Clean exit.

Then open you browser and go to http://localhost:8888

Also you can change address of flashlight server and engine:

    $ flashlight 192.168.0.1

or:

    $ flashlight 127.0.0.1 1

By default it uses address 127.0.0.1, port 9999 for flashlight server, port 8888 for websocket interface and protocol engine 2 (see code)

## Usage without install

If you want to run it without install in system, do the following:

    $ pip install tornado
    $ git clone https://github.com/skint/samples.git
    $ cd samples/flashlight/flashlight
    $ ./flashlight.py <address> <engine>
