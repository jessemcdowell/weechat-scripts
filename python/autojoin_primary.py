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
        """temp"""
        weechat.prnt(buffer, "list all")
    else:
        server = weechat.buffer_get_string(weechat.current_buffer(), "localvar_server")
        if server == "":
            """temp"""
            weechat.prnt(buffer, "%scommand \"%s\" must be run on irc buffer (server, channel, or private)" % (weechat.prefix("error"), SCRIPT_COMMAND))
            return weechat.WEECHAT_RC_ERROR
        weechat.prnt(buffer, "list for server: " + server)
    return weechat.WEECHAT_RC_OK

def autojoin_primary_cmd(data, buffer, args):
    """temp"""
    weechat.prnt(buffer, "data: " + data)
    weechat.prnt(buffer, "buffer: " + buffer)
    weechat.prnt(buffer, "args: " + args)

    split = args.split()
    if not split or split[0] == "list":
        return cmd_list(buffer, split[1:])
    weechat.prnt(buffer, "%scommand \"%s\" not recognized, see /help $s" % (weechat.prefix("error"), split[0], SCRIPT_COMMAND))
    return weechat.WEECHAT_RC_ERROR

if __name__ == "__main__" and import_ok:
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
        weechat.hook_command(SCRIPT_COMMAND, "Autojoin Primary Channels",
                 "[list] [-all]"
                 " || add <name>"
                 " || del <name>"
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
                 "autojoin_primary_cmd", "")
