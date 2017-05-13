from jinja2 import Template
import psycopg2
import os
import time
import json
import requests
from requests.exceptions import ConnectionError
import logging
import logging.handlers
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)
LOG_FILENAME = "log/fed_salary_log.log"

num_display = 20000
TABLE_NAME = "fed.federal_salaries"
YEAR = 2016

base_url = Template('https://www.fedsdatacenter.com/federal-pay-rates/output.php?iDisplayStart={{next_record_start}}&iDisplayLength={{num_display}}')


def setup_logger(file_log=False):
    if file_log is True:
        l = logging.getLogger()
        rotate_file_handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=1000000, backupCount=100)

        f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
        rotate_file_handler.setFormatter(f)
        l.addHandler(rotate_file_handler)

def remove_erroneous_chars(data_to_clean):
    chars_to_remove = {'comma': ',', 'dollar': '$'}

    logging.debug("Data before cleaning: {}".format(data_to_clean))
    separate_change = data_to_clean.split('.')
    final_sal = separate_change[0].replace(',', '')
    final_sal = final_sal.replace('$', '')
    cleaned_data = int(final_sal.replace('.', ''))
    logging.debug("Data after cleaning: {}".format(cleaned_data))

    return cleaned_data


def clean_data(data):
    logging.debug("All the data: {}".format(data))
    for i in data:
        logging.debug("Current record: {}".format(i))
        # Grade
        # TODO: More granular grade (some strings some numbers, separate)
        # i[1] = int(i[1])
        # logging.debug("Grade: {}". format(i[1]))

        # Salary
        i[3] = remove_erroneous_chars(i[3])
        logging.debug("Salary: {}". format(i[3]))
        # Bonus
        i[4] = remove_erroneous_chars(i[4])
        logging.debug("Bonus: {}". format(i[4]))
        # Year
        i[8] = int(i[8])
        logging.debug("Year: {}". format(i[8]))

    return data


def get_max_display_record():
    never_hit_record_count = 0

    # for display have some arbitrary ridiculous number
    url = base_url.render(next_record_start=never_hit_record_count, num_display=num_display, year=YEAR)
    print url
    headers = {'user-agent': 'python personal project app/0.0.1'}
    generated_url = requests.get(url, headers=headers)
    print generated_url.text
    get_data = json.loads(generated_url.text)
    get_max_record_count = get_data['iTotalDisplayRecords']

    return get_max_record_count


def get_paged_table_data(next_iter):
    url = base_url.render(next_record_start=next_iter, num_display=num_display, year=YEAR)
    print url
    try:
        generated_url = requests.get(url)
    except ConnectionError as e:
        logging.error(e)
        time.sleep(300)
        logging.error("Trying connecting again after sleep")
        generated_url = requests.get(url)
    print generated_url.text
    get_data = json.loads(generated_url.text)
    data = get_data['aaData']
    return data


import csv
f = open("data.csv", "a")
writer = csv.writer(f)

import time

def main():
    setup_logger(file_log=True)
    paging_count = int(get_max_display_record()) / num_display
    next_iter = 0

    while paging_count > 0:
        start = time.time()
        logging.info("Start processing data with paging count '{}'".format(paging_count))
        raw_data = get_paged_table_data(next_iter)
        logging.info("Paged records successfully pulled")
        cleaned_data = clean_data(raw_data)
        logging.info("Data cleaned!")
        #load_data(cleaned_data)
        #logging.info("Data with paging count '{}' finished processing!".format(paging_count))
        writer.writerows(cleaned_data)

        next_iter += num_display
        #logging.debug("Next iteration start number: {}".format(next_iter))
        print "Next iteration start number: {}".format(next_iter)
        paging_count -= 1
        # TODO: Add retry
        time.sleep(1)
        end = time.time()
        print(end - start)


if __name__ == "__main__":
    main()
