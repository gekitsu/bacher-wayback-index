#!/usr/bin/env python3

# scrapes tags metadata from hans bacher’s wordpress blog and saves it to
# ../data/tags.json

import json
import logging
import os
import requests


def is_content(response):
    """determine whether a JSON response has content.

    for tags: the API starts returning empty list"""
    try:
        assert response == []
        return False
    except (TypeError, AssertionError):
        return True


url = 'https://public-api.wordpress.com/wp/v2/sites/4826996/tags?page={page}'
out_fpath = '../data/tags.json'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('starting')
    page = 1
    data = []

    while True:
        logging.info('requesting page %s', page)
        req = requests.get(url.format(page=page))
        response = json.loads(req.text)
        if is_content(response):
            data += response
        else:
            logging.info('page %s did not contain more posts', page)
            break
        page += 1
    logging.info('writing to tags.json')
    with open(os.path.join(os.path.dirname(__file__), out_fpath), 'w') as f:
        json.dump(data, f, indent=1)
    logging.info('done')
