#!/usr/bin/env python
import os, sys, argparse, configparser, logging, multiprocessing.pool
import piwigo, commands


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs=1, help="Command to execute")

    """ upload command group """
    upload_group = parser.add_argument_group("upload")
    upload_group.add_argument("path", nargs="*", help="File or path to upload")
    upload_group.add_argument("-a", "--albums", help="Albums to upload to")
    upload_group.add_argument("-l", "--level", help="Privacy level [default: 8]")

    parser.add_argument(
        "--config",
        help="the location of the configuration file (default: ~/.piwigo-cli/config)",
        default=os.path.expanduser("~/.piwigo-cli/config"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log", help="increase output verbosity", default="INFO")

    args = parser.parse_args()

    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % args.log.upper())

    logging.basicConfig(level=numeric_level, format="%(levelname)s:\t%(message)s")

    config = configparser.ConfigParser()
    try:
        open(args.config)
        config.read(args.config)
    except:
        if not os.path.exists(os.path.dirname(args.config)):
            os.makedirs(os.path.dirname(args.config))
        config.add_section("piwigo")
        config.set("piwigo", "host", "")
        config.set("piwigo", "username", "")
        config.set("piwigo", "password", "")
        config.write(open(args.config, "w"))
        print("Please edit the configuration file: %s" % args.config)
        sys.exit(2)

    api = piwigo.api(config.get("piwigo", "host"))
    api.login(config.get("piwigo", "username"), config.get("piwigo", "password"))

    if args.command[0] == "upload":
        logging.debug("Running upload cmd")
        commands.upload_cmd(api, args)


if __name__ == "__main__":
    main()
