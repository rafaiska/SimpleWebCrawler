#!/usr/bin/env python3

import argparse

from src.simple_webcrawler import SimpleWebCrawler
from src.web_link import WebLink


def main():
    args = get_args()
    crawler = SimpleWebCrawler()
    crawler.configure(args)
    first = WebLink(args.url, None)
    crawler.add_link(first)
    crawler.queue_all_unvisited()
    crawler.crawl()


def get_args():
    parser = argparse.ArgumentParser(description='Simple Web Crawler')
    parser.add_argument('url', type=str, help='Starting URL')
    parser.add_argument('-n', dest='max_links', type=int, default=1000000, help='Max number of links to follow')
    parser.add_argument('-t', dest='max_subp', type=int, default=60, help='Max number of subprocesses to spawn')
    parser.add_argument('-w', dest='http_get_timeout', type=float, default=5.0, help='Timeout for HTTP GET (seconds)')
    parser.add_argument('-g', dest='global_timeout', type=float, default=1800.0, help='Global Timeout (seconds)')
    return parser.parse_args()


if __name__ == '__main__':
    main()
