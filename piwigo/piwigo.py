import requests, json, os, logging, hashlib
from piwigo import utils
from functools import partial
from multiprocessing.pool import Pool


class api:
    client = None
    host = None
    session = None

    def __init__(self, host):
        self.client = requests.Session()
        self.host = host

    def build_album_path(self, id, categories=None, path=[]):
        categories = self.get_categories() if categories is None else categories

        for category in categories:
            if category["id"] == id:
                path.insert(0, category["name"])
                if category["id_uppercat"]:
                    return self.build_album_path(
                        int(category["id_uppercat"]), categories, path
                    )

                return "/".join(path)

        return None

    def get_categories(self):
        response = self.client.post(
            "%s/ws.php?format=json" % self.host,
            data={"method": "pwg.categories.getList", "recursive": True},
        ).json()

        return response["result"]["categories"]

    def get_session_status(self):
        response = self.client.post(
            "%s/ws.php?format=json" % self.host,
            data={"method": "pwg.session.getStatus"},
        ).json()

        self.session = response
        return self.session

    def image_exists(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        md5 = hash_md5.hexdigest()

        response = self.client.post(
            "%s/ws.php?format=json" % self.host,
            data={"method": "pwg.images.exist", "md5sum_list": md5},
        ).json()

        return (
            response["result"][md5]
            if md5 in response["result"] and response["result"][md5]
            else False
        )

    def list_images(self, recursive=True, albums=""):
        params = {
            "method": "pwg.categories.getImages",
            "recursive": recursive,
            "cat_id": "|".join(albums.split(",")) if len(albums) != 0 else "",
            "per_page": 500,
            "order": "file",
        }

        page = 0
        photos = []
        while True:
            params["page"] = page
            response = self.client.post(
                "%s/ws.php?format=json" % self.host, data=params
            ).json()
            if len(response["result"]["images"]) == 0:
                break
            photos += response["result"]["images"]
            page += 1

        return photos

    def login(self, username, password):
        logging.debug("Logging in...")
        response = self.client.post(
            "%s/ws.php?format=json" % self.host,
            data={
                "method": "pwg.session.login",
                "username": username,
                "password": password,
            },
        ).json()

        self.get_session_status()

        return response

    def set_image_info(self, id, data={}):
        data["method"] = "pwg.images.setInfo"
        data["image_id"] = id

        response = self.client.post(
            "%s/ws.php?format=json" % self.host, data=data
        ).json()

        return response

    def upload_file(self, filepath, level=8, categories=""):
        form = {
            "method": "pwg.images.upload",
            "name": os.path.basename(filepath),
            "pwg_token": self.session["result"]["pwg_token"],
            "category": "|".join(categories.split(",")),
            "level": level,
        }

        logging.info("Uploading %s..." % filepath)
        with open(filepath, "rb") as stream:
            response = self.client.post(
                "%s/ws.php?format=json" % self.host, form, files={"file": stream}
            )

        logging.debug(response.content)
        try:
            retval = response.json()
        except json.decoder.JSONDecodeError:
            retval = {"stat": "fail", "message": str(response.content)}

        return retval
