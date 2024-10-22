#
# Copyright (c) 2024 Jesse McDowell <jessemcd1@gmail.com>
#
# autojoin_primary: A smaller autojoin list for your primary channels
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <https://www.gnu.org/licenses/>.
#
# 2024-10-22: Jesse McDowell
#     version 1.0: Initial release

SCRIPT_NAME    = "autojoin_primary"
SCRIPT_AUTHOR  = "Jesse McDowell <jessemcd1@gmail.com>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "A smaller autojoin list for your primary channels"
SCRIPT_COMMAND = SCRIPT_NAME

import_ok = True

try:
    import weechat
except:
    print("This script must be run under WeeChat.")
    import_ok = False

def cmd_list(buffer, args):
    if "-all" in args:
        weechat.prnt("", "Primary autojoin list for all servers:")
        any = False
        server_list = weechat.infolist_get("irc_server", "", "")
        while weechat.infolist_next(server_list):
            server = weechat.infolist_string(server_list, "name")
            for channel in get_autojoin_list(server):
                weechat.prnt("", "  %s @ %s" % (channel, server))
                any = True
        if not any:
            weechat.prnt("", "  (none)")

    else:
        server, server_buffer = get_server(buffer, "list")
        if server == "":
            return weechat.WEECHAT_RC_ERROR

        server_buffer = weechat.info_get("irc_buffer", server)
        weechat.prnt(server_buffer, "Primary autojoin list for %s:" % server)
        any = False
        for channel in get_autojoin_list(server):
            weechat.prnt(server_buffer, "  %s" % channel)
            any = True
        if not any:
            weechat.prnt(server_buffer, "  (none)")
    return weechat.WEECHAT_RC_OK

def cmd_join_server(server, server_buffer):
    autojoin_list = get_autojoin_list(server)
    for channel in autojoin_list:
        weechat.command(server_buffer, "/join %s" % channel)
    return weechat.WEECHAT_RC_OK

def cmd_join(buffer, args):
    if "-all" in args:
        server_list = weechat.infolist_get("irc_server", "", "")
        while weechat.infolist_next(server_list):
            if weechat.infolist_integer(server_list, "is_connected"):
                server = weechat.infolist_string(server_list, "name")
                server_buffer = weechat.infolist_pointer(server_list, "buffer")
                cmd_join_server(server, server_buffer)
    else:
        server, server_buffer = get_server(buffer, "list")
        if server == "":
            return weechat.WEECHAT_RC_ERROR
        return cmd_join_server(server, server_buffer)
    return weechat.WEECHAT_RC_OK

def cmd_only_server(server, server_buffer):
    primary_autojoin_list = get_autojoin_list(server)
    channel_list = weechat.infolist_get("irc_channel", "", server)
    while weechat.infolist_next(channel_list):
        channel = weechat.infolist_string(channel_list, "name")
        if not channel in primary_autojoin_list:
            weechat.command(server_buffer, "/close %s" % channel)
    return weechat.WEECHAT_RC_OK

def cmd_only(buffer, args):
    if "-all" in args:
        server_list = weechat.infolist_get("irc_server", "", "")
        while weechat.infolist_next(server_list):
            if weechat.infolist_integer(server_list, "is_connected"):
                server = weechat.infolist_string(server_list, "name")
                server_buffer = weechat.infolist_pointer(server_list, "buffer")
                cmd_only_server(server, server_buffer)
    else:
        server, server_buffer = get_server(buffer, "list")
        if server == "":
            return weechat.WEECHAT_RC_ERROR
        return cmd_only_server(server, server_buffer)
    return weechat.WEECHAT_RC_OK

def cmd_add(buffer, args):
    server, server_buffer = get_server(buffer, "add")
    if server == "":
        return weechat.WEECHAT_RC_ERROR

    if (not args):
        weechat.prnt(server_buffer, "%sYou must specify at least one channel to add to primary autojoin list" % weechat.prefix("error"))

    for channel in args:
        if not weechat.info_get("irc_is_channel", channel):
            weechat.prnt(server_buffer, "%s\"%s\" is not a valid channel name for irc" % (weechat.prefix("error"), channel))
            return weechat.WEECHAT_RC_ERROR

    primary_autojoin_list = get_autojoin_list(server)
    any = False
    for channel in args:
        if channel not in primary_autojoin_list:
            primary_autojoin_list.append(channel)
            any = True
        else:
            weechat.prnt(server_buffer, "%sChannel \"%s\" is already in primary autojoin list" % (weechat.prefix("error"), channel))
    if any:
        set_autojoin_list(server, primary_autojoin_list)
        weechat.prnt(server_buffer, "Primary auto-join list updated to: %s" % ", ".join(primary_autojoin_list))
        return weechat.WEECHAT_RC_OK
    return weechat.WEECHAT_RC_ERROR

def cmd_del(buffer, args):
    server, server_buffer = get_server(buffer, "add")
    if server == "":
        return weechat.WEECHAT_RC_ERROR

    if (not args):
        weechat.prnt(server_buffer, "%sYou must specify at least one channel to delete from primary autojoin list" % weechat.prefix("error"))

    primary_autojoin_list = get_autojoin_list(server)
    any = False
    for channel in args:
        if channel in primary_autojoin_list:
            primary_autojoin_list.remove(channel)
            any = True
        else:
            weechat.prnt(server_buffer, "%sChannel \"%s\" is not in primary autojoin list" % (weechat.prefix("error"), channel))
    if any:
        set_autojoin_list(server, primary_autojoin_list)
        weechat.prnt(server_buffer, "Primary auto-join list updated to: %s" % ", ".join(primary_autojoin_list))
        return weechat.WEECHAT_RC_OK
    return weechat.WEECHAT_RC_ERROR

def get_server(buffer, command):
    server = weechat.buffer_get_string(buffer, "localvar_server")
    if server == "":
        weechat.prnt("", "%s/%s %s must be run on irc buffer (server, channel, or private)" % (weechat.prefix("error"), command, SCRIPT_COMMAND))
        return ("", "")
    server_buffer = weechat.info_get("irc_buffer", server)
    return (server, server_buffer)

def get_autojoin_list(server):
    text = weechat.config_get_plugin("%s.autojoin" % server)
    if not text:
        return []
    return text.split(",")

def set_autojoin_list(server, channel_list):
    if channel_list:
        text = ",".join(channel_list)
    else:
        text = ""
    weechat.config_set_plugin("%s.autojoin" % server, text)

def autojoin_primary_cb(_, buffer, args):
    split = args.split()
    if not split or split[0] == "list":
        return cmd_list(buffer, split[1:])
    if split[0] == "add":
        return cmd_add(buffer, split[1:])
    if split[0] == "del":
        return cmd_del(buffer, split[1:])
    if split[0] == "join":
        return cmd_join(buffer, split[1:])
    if split[0] == "only":
        return cmd_only(buffer, split[1:])
    weechat.prnt("", "%s/%s %s not recognized, see /help %s" % (weechat.prefix("error"), SCRIPT_COMMAND, split[0], SCRIPT_COMMAND))
    return weechat.WEECHAT_RC_ERROR

if __name__ == "__main__" and import_ok:
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
        weechat.hook_command(SCRIPT_COMMAND, "Autojoin Primary Channels",
                 "[list] [-all]"
                 " || add <name> [<channel>...]"
                 " || del <name> [<channel>...]"
                 " || join [-all]"
                 " || only [-all]",
                 "      list: list all primary channels\n"
                 "       add: add a primary channel\n"
                 "       del: delete a primary channel\n"
                 "      join: join all primary channels\n"
                 "      only: join only primary channels (leave all others)\n"
                 "\n"
                 "Without argument, this command lists primary channels for the current server.\n"
                 "\n"
                 "Examples:\n"
                 f"  Add a primary channel:                                 /{SCRIPT_COMMAND} add #myroom\n"
                 f"  Join primary channels on all servers:                  /{SCRIPT_COMMAND} join -all\n"
                 f"  Leave all non-primary channels on the current server:  /{SCRIPT_COMMAND} only\n",
                 "list -all"
                 " || add %(channel)"
                 " || del %(channel)"
                 " || join -all"
                 " || only [-all]",
                 "autojoin_primary_cb", "")
