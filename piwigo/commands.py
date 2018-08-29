import logging, os, re
from piwigo import utils
from functools import partial
from multiprocessing.pool import Pool
from datetime import datetime


def upload_file(args, api, dirpath, file):
    # skip json data files
    if re.search("\.json$", file):
        return

    if api.image_exists("%s/%s" % (dirpath, file)):
        logging.info("%s exists, skipping." % file)
    else:
        if args.dry_run:
            logging.info("Dry run, not uploading %s" % file)
        else:
            response = api.upload_file(
                "%s/%s" % (dirpath, file), args.level, args.albums
            )
            if response["stat"] == "ok":
                mtime = os.path.getmtime("%s/%s" % (dirpath, file))
                api.set_image_info(
                    response["result"]["image_id"],
                    {
                        "date_creation": datetime.fromtimestamp(mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "single_value_mode": "replace",
                        "multiple_value_mode": "replace",
                    },
                )


def upload_cmd(api, args):
    for path in args.path:
        path = utils.full_path(path)
        if os.path.isfile(path):
            upload_file(args, api, os.path.dirname(path), os.path.basename(path))
        for (dirpath, dirnames, filenames) in os.walk(path):
            upload = partial(upload_file, args, api, dirpath)
            # for file in filenames:
            #     upload_file(args, api, dirpath, file)
            with Pool(2) as p:
                p.map(upload, filenames)


def list_albums_cmd(api, args):
    albums = api.get_categories()
    for album in albums:
        logging.info(
            "{}\t{}".format(album["id"], api.build_album_path(album["id"], albums, []))
        )
