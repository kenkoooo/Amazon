import csv
import json
import threading
import urllib.request
import urllib.error
from datetime import datetime

import time

from io import StringIO
from bottle import get, response, run, static_file, route
from bs4 import BeautifulSoup


def get_html_bs(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    })
    html = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(html, "html.parser")
    return soup


def crawl(node, num):
    num = int(num)
    products = []
    page = 1
    max_page = int((num + 24) / 24)
    while page <= max_page:
        print(page)
        prev = len(products)

        try:
            url = "https://www.amazon.co.jp/b?ie=UTF8&node={node}&page={page}".format(page=page, node=node)
            print(url)
            bs = get_html_bs(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            continue
        except Exception as e:
            print("Parser")
            print(e)
            continue

        for item in bs.find_all("div", attrs={"class": "s-item-container"}):
            product = {}

            try:
                price = item.find("span", attrs={"class": "s-price"}).get_text()
                price = price.replace("￥ ", "")
                price = price.replace(",", "")
                product["price"] = int(price)
            except Exception as e:
                print("Price Error")
                print(e)
                product["price"] = -1

            try:
                title = item.find("h2").get_text()
                product["title"] = title.replace(",", " ")
            except Exception as e:
                print("Title Error")
                print(e)
                product["title"] = ""

            product["brand"] = ""
            try:
                for div in item.find_all("div", attrs={"class", "a-row a-spacing-none"}):
                    spans = div.find_all("span", attrs={"class": "a-size-small a-color-secondary"})
                    if len(spans) != 2:
                        continue

                    if len(spans[0].get_text()) != 0:
                        continue

                    product["brand"] = spans[1].get_text()
            except Exception as e:
                print("Brand Error")
                print(e)

            products.append(product)
        if len(products) == prev:
            break

        time.sleep(0.3)
        page += 1
    return products


class Crawler(threading.Thread):
    def __init__(self):
        super().__init__()
        self.queue = []
        self.results = {}
        self.status = {}
        self.dates = {}

    def run(self):
        while True:
            if len(self.queue) == 0:
                time.sleep(1)
                continue

            node, num = self.queue[0]
            self.queue.pop(0)

            key = str(node) + "-" + str(num)
            self.status[key] = "running"
            try:
                self.results[key] = crawl(node, num)
                self.status[key] = "done"
            except Exception as e:
                self.status[key] = "error"
                print(e)

    def push(self, node, num):
        self.queue.append((node, num))
        key = str(node) + "-" + str(num)
        self.status[key] = "pending"
        self.dates[key] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        return key

    def get_csv(self, key):
        if key not in self.results:
            return "Not Found"

        try:
            response.content_type = 'application/octet-stream'
            response.headers['Content-Disposition'] = "attachment; filename='{key}.csv'".format(key=key)
            stream = StringIO()
            writer = csv.writer(stream)
            writer.writerow(["title", "brand", "price"])
            for p in self.results[key]:
                writer.writerow([p["title"], p["brand"], p["price"]])
            stream.seek(0)
            csv_binary = stream.getvalue().encode('shift-jis', "ignore")
            return csv_binary
        except Exception as e:
            print(e)
            response.content_type = 'application/text'
            lines = "title,brand,price\n"
            for p in self.results[key]:
                lines = lines + p["title"] + "," + p["brand"] + "," + str(p["price"]) + "\n"
            return lines

    def debug(self):
        return json.dumps(self.queue)

    def get_status(self):
        statuses = []
        for k, v in self.status.items():
            statuses.append({"key": k, "status": v, "date": self.dates[k]})
        response.content_type = 'application/json'
        statuses = sorted(statuses, key=lambda x: x["date"])
        return json.dumps(statuses)


@route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root="./static")


@route("/")
def root():
    return static("index.html")


def main():
    crawler = Crawler()
    get("/status")(crawler.get_status)
    get("/debug")(crawler.debug)
    get("/csv/:key")(crawler.get_csv)
    get("/push/:node/:num")(crawler.push)
    crawler.start()
    run(host="0.0.0.0", port=12345, debug=True)


if __name__ == '__main__':
    main()
