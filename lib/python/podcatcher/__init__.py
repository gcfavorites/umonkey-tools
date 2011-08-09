#/usr/bin/env python
# encoding=utf-8

import json
import logging
import os
import time

import feedparser
import yaml


CONFIG_FILE = "podcatcher.yaml"
STATUS_FILE = "podcatcher.json"


def log(message):
    print message


class Status(dict):
    def load(self):
        self.clear()
        if os.path.exists(STATUS_FILE):
            self.update(json.loads(STATUS_FILE))

    def save(self):
        file(STATUS_FILE, "wb").write(json.dumps(self, ensure_ascii=False, indent=True).encode("utf-8"))


class Subscription(dict):
    def __init__(self):
        self.config = CONFIG_FILE
        self.reload()

    def reload(self):
        self.clear()

        if os.path.exists(self.config):
            items = yaml.load(file(self.config, "rb")).get("feeds", {})
            for item in items:
                self[item["url"]] = item

    def update(self, status, feed_urls=None):
        for url, feed in sorted(self.items()):
            if url not in status:
                status[url] = {}
            status[url]["last_updated"] = time.time()
            self.update_feed(status[url], url)
            if "name" in feed:
                status[url]["title"] = feed["name"]

    def update_feed(self, data, url):
        log("Checking %s" % url)

        if "entries" not in data:
            data["entries"] = {}

        feed = feedparser.parse(url, etag=data.get("etag"),
            modified=data.get("last-modified"))
        if feed["status"] != 200:
            print "skipped feed: wrong status: %s" % feed["status"]
            return data

        if "headers" in feed:
            tmp = feed["headers"]
            if "etag" in tmp:
                data["etag"] = tmp["etag"]
            if "last-modified" in tmp:
                data["last-modified"] = tmp["last-modified"]

        if "feed" in feed:
            tmp = feed["feed"]
            if tmp.get("title"):
                data["title"] = tmp["title"]
            if tmp.get("subtitle"):
                data["subtitle"] = tmp["subtitle"]
            if tmp.get("summary"):
                data["summary"] = tmp["summary"]
            if tmp.get("iamge") and "href" in tmp["image"]:
                data["image"] = tmp["image"]["href"]

        if "entries" in feed:
            for entry in feed["entries"]:
                item = { }

                field_map = {
                    "title": "title",
                    "subtitle": "summary",
                    "summary": "summary_raw",
                    "author": "author",
                    "link": "link",
                    "image": "image",
                    "enclosures": "enclosures",
                }

                for k, v in field_map.items():
                    tmp = entry.get(k)
                    if tmp:
                        item[v] = tmp

                if "enclosures" not in item:
                    log("skip entry: no enclosures: %s" % item["link"])
                    continue

                item_id = entry.get("id", entry.get("link"))
                data["entries"][item_id] = item

        return data


class Client(object):
    def __init__(self):
        self.subscription = Subscription()
        self.status = Status()

    def update(self, feed_urls=None):
        self.subscription.update(self.status, feed_urls)
        self.status.save()


if __name__ == "__main__":
    cli = Client()
    cli.update()
