import configparser
import sys
import pymongo
import os

from dateutil import parser
from display_tools.display_tools import TextOutput as output
from html.parser import HTMLParser
from pymongo import MongoClient
from urllib.request import urlopen

BASE_URL = 'https://golfshot.com/profiles/'
CONFIG_FILE = './golfshot.cfg'
# https://play.golfshot.com/profiles/Vm65JW/rounds



class HtmlListReader(HTMLParser):
    def __init__(self, source):
        self.in_list = False
        self.page_data = False
        self.round_data = {}
        self.pages = []
        self.current_round = ''
        HTMLParser.__init__(self)
        if source.startswith('http'):
            req = urlopen(source)
            self.feed(req.read().decode('utf-8'))
        else:
            with open(source, 'r') as file:
                self.feed(file.read())

    def handle_starttag(self, tag, attrs):
        if tag == 'tr' and attrs:
            self.current_round = attrs[0][1]
            self.round_data[self.current_round] = []
            self.in_list = True
        elif tag == 'td' and attrs:
            pass
        elif tag == 'div' and attrs[0][0] == 'class' and attrs[0][1] == 'pagination':
            self.page_data = True

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.in_list = False
        elif tag == 'div':
            self.page_data = False

    def handle_data(self, data):
        if self.in_list and data.strip() != '':
            self.round_data[self.current_round].append(data.strip())
        elif self.page_data and data.strip() != '' and data.strip() != 'Previous' and data.strip() != 'Next':
            self.pages.append(data.strip())


class GolfShotExporter():

    def __init__(self):
        self.config = initialize_config()
        connection = MongoClient(self.config.get('db', 'url'))
        db = connection.gs_data
        self.rounds = db.rounds

    def pull_golfshot_data(self, golfer_data):
        for golfer in golfer_data:
            output.header('Getting round data for %s' % golfer)
            source = BASE_URL + golfer_data[golfer] + '/rounds'
            if self.config.getboolean('local', 'read_from_local'):
                source = os.path.join(os.getcwd(), self.config.get('local', 'local_file_path'))
            self.golf_shot_reader = HtmlListReader(source)
            round_info = {}
            for page in self.golf_shot_reader.pages:
                source = BASE_URL + golfer_data[golfer] + '/rounds?page=' + page
                if self.config.getboolean('local', 'read_from_local'):
                    source = os.path.join(os.getcwd(), self.config.get('local', 'local_file_path'))
                data = HtmlListReader(source)

                round_info = self.write_to_db(golfer, data.round_data)
            print(round_info)

    @staticmethod
    def normalize_round_data(round_data):
        normalized_rounds = []
        for info in round_data:
            normalized_round_data = {}
            if len(round_data[info]) != 6:
                continue

            normalized_round_data['_id'] = info
            normalized_round_data['date'] = parser.parse(round_data[info][0])
            normalized_round_data['course'] = round_data[info][1]
            normalized_round_data['score'] = int(round_data[info][2])
            normalized_round_data['fwy'] = float(round_data[info][3])
            normalized_round_data['gir'] = float(round_data[info][4])
            normalized_round_data['putt_gir'] = float(round_data[info][5])

            normalized_rounds.append(normalized_round_data)

        return normalized_rounds

    def write_to_db(self, golfer_name, round_data):
        normalized_rounds = self.normalize_round_data(round_data)
        for golf_round in normalized_rounds:
            golf_round['golfer_name'] = golfer_name
            try:
                self.rounds.insert_one(golf_round)
            except pymongo.errors.DuplicateKeyError:
                output.warn('Skipping...round already exists in golfshot DB')
                continue
            except Exception as e:
                output.error('Unknown error occurred during DB insertion')
                output.msg(e)
                continue

            output.info('Successfully inserted round:')
            output.dict(golf_round)

    def Run(self):
        self.pull_golfshot_data(dict(self.config.items('Golfers')))


def main():
    golf_shot_export = GolfShotExporter()
    golf_shot_export.Run()

def initialize_config():
    """Initialize the golfshot config file."""
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE)
    except IOError as e:
        print('Error reading %s: %s' % (CONFIG_FILE, e))
        exit(1)

    return config


if __name__ == '__main__':
    main()
