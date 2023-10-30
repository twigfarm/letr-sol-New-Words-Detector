import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem


# mongo_db 설정
class DcPipeline(object):

    def process_item(self, item, spider):
        return item
