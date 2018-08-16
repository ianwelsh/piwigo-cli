import logging, os, utils
from functools import partial
from multiprocessing.pool import Pool

def upload_file(args, api, dirpath, file):
    if api.image_exists("%s/%s" % (dirpath, file)):
        logging.info("%s exists, skipping." % file)
    else:
        if args.dry_run:
            logging.info("Dry run, not uploading %s" % file)
        else:
            api.upload_file("%s/%s" % (dirpath, file), args.level, args.albums)

def upload_cmd(api, args):
    for path in args.path:
        path = utils.full_path(path)
        if os.path.isfile(path):
            upload_file(args, api, os.path.dirname(path), os.path.basename(path))
        for (dirpath, dirnames, filenames) in os.walk(path):
            upload = partial(upload_file, args, api, dirpath)
            with Pool(1) as p:
                p.map(upload, filenames)
