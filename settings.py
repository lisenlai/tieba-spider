BOT_NAME = 'tiebaSpider'

SPIDER_MODULES = ['tiebaSpider.spiders']
NEWSPIDER_MODULE = 'tiebaSpider.spiders'
LOG_LEVEL = "ERROR"

ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'tiebaSpider.middlewares.seleniumDownloadMiddleware': 543,
}

ITEM_PIPELINES = {
    'tiebaSpider.pipelines.MysqlPipeline': 300,
}