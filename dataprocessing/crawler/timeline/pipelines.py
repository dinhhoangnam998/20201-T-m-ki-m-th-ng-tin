# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from datetime import datetime
class StopIfSeeDuplicate:
    def open_spider(self, spider):
        with open('state.json', 'r') as f:
            state = json.load(f)
            if 'last_time' in state:
                self.this_time = self.last_time = datetime.strptime(state['last_time'], r"%H:%M %d/%m/%Y")
            else:
                self.this_time = self.last_time = datetime(2000,1,1)

    def close_spider(self, spider):
        with open('state.json', 'w') as f:
            json.dump({'last_time': datetime.strftime(self.this_time, r"%H:%M %d/%m/%Y")}, f)

    def process_item(self, item, spider):
        item_time = datetime.strptime(item['time'], r"%H:%M %d/%m/%Y")

        if item_time > self.last_time:
            if item_time > self.this_time:
                self.this_time = item_time
            return item
            
        if item_time <= self.last_time:
            spider.crawler.engine.close_spider(self, reason='duplicate...')

from scrapy.exporters import JsonLinesItemExporter
class JsonWriterPipeline:
    def open_spider(self, spider):
        timestamp = datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S')
        file_name = 'data/timeline_data_' + timestamp + '.jl'
        self.file = open(file_name, 'wb')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8')

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
