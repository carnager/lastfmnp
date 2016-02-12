"""
    lastfmnp.py

    author: i7c <i7c AT posteo PERIOD de>
    version: 0.1
    license: GPLv3

Description:
    lastfmnp.py can say the currently played song  by a last.fm user to a
    buffer. It requires a valid API key for the last.fm API. This plugin does
    not provide the key, you may obtain one from last.fm.

    lastfmnp.py provides one command: /lastfmnp

    If no argument is provided, it will retrieve the currenctly playing song by
    last.fm user set in "plugins.var.python.lastfmnp.user". With one argument
    it will retrieve the song of that user, like so:

    /lastfmnp iSevenC

    The script will say the message set in the npstring option if a song is and
    the message in the nothing option otherwise. [who], [artist] and [title]
    are replaced by the respective values ([who] being "/me" or the user you
    queried). In the nothing message, only [who] is replaced.
"""
import weechat
import pylast

SCRIPT = "lastfmnp"
CONF_PREFIX = "plugins.var.python." + SCRIPT + "."
CONFKEY_APIKEY = "apikey"
CONFKEY_NPSTRING = "npstring"
CONFKEY_NPSTRING_ALBUM = "npstring_album"
CONFKEY_USER = "user"
CONFKEY_WHO = "who"

REPLACE_MAP = {
        "who": u"[who]",
        "title": u"[title]",
        "artist": u"[artist]",
        "album": u"[album]"
        }

"""
    Formats an np string
"""
def format_message(template, **kwargs):
    result = template
    for k,v in kwargs.iteritems():
        if k in REPLACE_MAP:
            result = result.replace(REPLACE_MAP[k], v)
        else:
            weechat.prnt("", "Unknown key: " + k)
    return result

"""
    Retrieves the np information for who. If who is not set, retrieve for user
    set in the configuration opitons.
"""
def lastfm_retrieve(who = None):
    api_key = weechat.config_string(weechat.config_get(CONF_PREFIX
        + CONFKEY_APIKEY))
    username = weechat.config_string(weechat.config_get(CONF_PREFIX
        + CONFKEY_USER))
    npinfo = {}

    network = pylast.LastFMNetwork(api_key = api_key)
    if who:
        user = network.get_user(who)
    else:
        user = network.get_user(username)
    np = user.get_now_playing()
    if not np:
        return {}
    npinfo["title"] = np.title
    npinfo["artist"] = np.artist.name
    if np.get_album():
        npinfo["album"] = album = np.get_album().get_title()
    return npinfo

"""
    Command to be called by weechat user: /lastfmnp
"""
def lastfmnp(data, buffer, args):
    who = weechat.config_string(weechat.config_get(CONF_PREFIX
        + CONFKEY_WHO))
    message_default = weechat.config_string(weechat.config_get(CONF_PREFIX
        + CONFKEY_NPSTRING))
    message_album = weechat.config_string(weechat.config_get(CONF_PREFIX
        + CONFKEY_NPSTRING_ALBUM))

    if len(args) > 0:
        # which song is someone else playing (lastfmnp command with argument)
        np = lastfm_retrieve(args)
        msg = format_message(message_default, who=unicode(args), **np)
    else:
        # which song am I playing?
        np = lastfm_retrieve()
        if "album" in np:
            msg = format_message(message_album, who=unicode(who), **np)
        elif np:
            msg = format_message(message_default, who=unicode(who), **np)
        else:
            weechat.prnt("", "lastfmnp: API response was empty or invalid.")
    if len(msg) > 0:
        weechat.command(buffer, msg.encode("utf-8"))
    return weechat.WEECHAT_RC_OK


"""
    Initialization for Weechat
"""
weechat.register(SCRIPT, "i7c", "0.1", "GPL3",
        "Prints currently playing song from last.fm", "", "")

weechat.hook_command("lastfmnp", "prints currently playing song",
        "[username]", "username: lastfm username", "lastfmnp", "lastfmnp", "")

script_options = {
        CONFKEY_NPSTRING: "[who] np: [artist] - [title]",
        CONFKEY_NPSTRING_ALBUM: "[who] np: [artist] - [title] ([album])",
        CONFKEY_APIKEY: "",
        CONFKEY_USER: "",
        CONFKEY_WHO: "/me"}

for option, default in script_options.items():
    if not weechat.config_is_set_plugin(option):
        weechat.config_set_plugin(option, default)

