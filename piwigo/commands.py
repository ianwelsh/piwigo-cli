import logging, os, re, requests
from piwigo import utils
from functools import partial
from multiprocessing.pool import Pool
from datetime import datetime

class Downloader(object):
    def __init__(self, save_dir):
        self.save_dir = save_dir
    def __call__(self, image):
        if os.path.isfile("{}/{} - {}".format(self.save_dir, image['id'], image['file'])):
            print("File {} - {} exists. Skipping.".format(image['id'], image['file']))
            return

        print("Downloading {}".format(image['file']))
        dl = requests.get(image["element_url"], stream=True)
        with open(
            "{}/{} - {}.dl".format(self.save_dir, image["id"], image["file"]), "wb"
        ) as handle:
            for data in dl.iter_content(chunk_size=512):
                handle.write(data)
            handle.close()
            dl.close()

        os.rename(
            "{}/{} - {}.dl".format(self.save_dir, image["id"], image["file"]),
            "{}/{} - {}".format(self.save_dir, image["id"], image["file"]),
        )

def download_images_cmd(api, args):
    images = api.list_images(args.recursive, args.albums)
    if not os.path.isdir(args.save_dir):
        os.makedirs(args.save_dir)

    with Pool() as p:
        p.map(Downloader(args.save_dir), images)

def list_images_cmd(api, args):
    args.albums = args.albums or ""
    images = api.list_images(args.recursive, args.albums)
    for image in images:
        print(image)


def upload_file(args, api, dirpath, file):
    # skip json data files
    if re.search("\.json$", file):
        return

    fullpath = "%s/%s" % (dirpath, file)

    if api.image_exists(fullpath):
        logging.info("%s exists, skipping." % file)
        if args.remove_source_files == True:
            os.remove(fullpath)
    else:
        if args.dry_run:
            logging.info("Dry run, not uploading %s" % file)
        else:
            response = api.upload_file(fullpath, args.level, args.albums)
            if response["stat"] == "ok":
                mtime = os.path.getmtime(fullpath)
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
                if args.remove_source_files == True:
                    os.remove(fullpath)


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
