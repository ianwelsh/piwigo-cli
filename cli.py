#!/usr/bin/env python
#!/usr/bin/env python
import os, sys, argparse, configparser, logging, commands, piwigo

config = {
    "upload": {"desc": "Upload media"},
    "albums": {"desc": "Perform actions with albums"},
}


class cli:
    config = None
    api = None

    def __init__(self):
        usage = """piwigo <command> [<args>]

Commands
"""

        for command in config:
            usage = "{}  {}\t{}\n".format(usage, command, config[command]["desc"])

        parser = argparse.ArgumentParser(usage=usage)
        parser.add_argument("command", help="Command to execute")
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print("Invalid command %s" % args.command)
            parser.print_help()
            exit(1)

        getattr(self, args.command)()

    def read_config(self, args):
        self.config = configparser.ConfigParser()
        try:
            open(args.config)
            self.config.read(args.config)
        except:
            if not os.path.exists(os.path.dirname(args.config)):
                os.makedirs(os.path.dirname(args.config))
            self.config.add_section("piwigo")
            self.config.set("piwigo", "host", "")
            self.config.set("piwigo", "username", "")
            self.config.set("piwigo", "password", "")
            self.config.write(open(args.config, "w"))
            print("Please edit the configuration file: %s" % args.config)
            sys.exit(2)

    def add_global_opts(self, parser):
        parser.add_argument(
            "--config",
            help="The location of the configuration file",
            default=os.path.expanduser("~/.piwigo-cli/config"),
        )
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--log", help="increase output verbosity", default="INFO")
        return parser

    def upload(self):
        parser = argparse.ArgumentParser(
            usage="piwigo upload <path> [<args>]", description="Upload images"
        )
        parser.add_argument("path", nargs="*", help="Username(s)")
        parser.add_argument("-a", "--albums", help="Albums to upload to")
        parser.add_argument("--level", help="Privacy level [default: 8]")
        parser = self.add_global_opts(parser)
        args = parser.parse_args(sys.argv[2:])

        self.setup(args)

        commands.upload_cmd(self.api, args)

    def albums(self):
        parser = argparse.ArgumentParser(
            usage="piwigo albums [<args>]", description="Perform actions with albums"
        )
        parser.add_argument("-l", "--list", action="store_true", help="List all albums")
        parser = self.add_global_opts(parser)
        args = parser.parse_args(sys.argv[2:])

        self.setup(args)

        commands.list_albums_cmd(self.api, args)

    def setup(self, args):
        numeric_level = getattr(logging, args.log.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError("Invalid log level: %s" % args.log.upper())

        logging.basicConfig(level=numeric_level, format="%(levelname)s:\t%(message)s")

        self.read_config(args)

        self.api = piwigo.api(self.config.get("piwigo", "host"))
        self.api.login(
            self.config.get("piwigo", "username"), self.config.get("piwigo", "password")
        )


if __name__ == "__main__":
    cli()
