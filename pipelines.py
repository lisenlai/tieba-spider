# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from tiebaSpider.items import TieItem
from tiebaSpider.items import FloorItem
from tiebaSpider.items import FloorFloorItem
import pymysql

class MysqlPipeline:
    conn = None
    cursor = None
    def open_spider(self, spider):
        #打开管道，连接到mysql数据库，如果没有user,video和followfans数据表，就创建
        user = "root"
        password = ""
        database = "tieba"
        port = 3306
        self.conn = pymysql.Connect(host='127.0.0.1', port = port, user = user, password = password, db=database,charset='utf8mb4')
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""create table if not exists `tie`(
                tie_id bigint primary key,
                author char(50),
                title char(255),
                time char(50))
                """)
            self.cursor.execute("""create table if not exists `floor`(
                tie_id bigint,
                floor_num int,
                author char(50),
                content text,
                time char(50))
                """)
            self.cursor.execute("""create table if not exists `floorfloor`(
                tie_id bigint,
                floor_num int,
                author char(50),
                content text,
                time char(50))
                """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()


    def process_item(self, item, spider):
        if isinstance(item, TieItem):
            sql = """
                    replace into `tie` (tie_id, author, title, time)
                    values(%s, %s, %s, %s)
                  """
            self.cursor.execute(sql, (item['tie_id'], item['author'], item['title'], item['time']))
        elif isinstance(item, FloorItem):
            sql = """
                    insert into `floor` (tie_id, floor_num, author, content, time)
                    values(%s, %s, %s, %s, %s)
                  """
            self.cursor.execute(sql, (item['tie_id'], item['floor_num'], item['author'], item['content'], item['time']))
        elif (isinstance(item, FloorFloorItem)):
            sql = """
                    insert into `floorfloor` (tie_id, floor_num, author, content, time)
                    values(%s, %s, %s, %s, %s)
                  """
            self.cursor.execute(sql, (item['tie_id'], item['floor_num'], item['author'], item['content'], item['time']))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        #关闭数据库的连接
        self.cursor.close()
        self.conn.close()
