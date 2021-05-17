## amazon-spider

一个简单的增量式爬虫，用于增量式爬取百度某吧的前5页内容。去重方面，使用redis的set保存爬取内容的唯一标识，并使用mysql进行持久化存储

## 开发环境

- Python: `3.6.6`
- Scrapy: `2.5.0`
- Mysql: `8.0.24`
- redis: `5.0.10`

## 注意事项

- 根据你的谷歌浏览器版本从<http://chromedriver.storage.googleapis.com/index.html>下载安装浏览器驱动
- Windows用户安装Scrapy可能出错，你可以根据以下步骤安装Scrapy：
    - `pip install wheel`
    - 下载twisted: 从<https://www.lfd.uci.edu/~gohlke/pythonlibs/>找到对应的wheel文件下载
    - cd到下载文件所在目录,使用`pip install 文件名`安装twisted
    - `pip install pywin32`
    - `pip install scrapy`
- 使用`pip install -r requirements.txt`安装项目所有依赖包
- 构建ip池所使用的ip来自<https://www.engeniusiot.com/pricing>，无论使用哪家网站的套餐，记得在middlewares.py
里seleniumDownloadMiddleware类的update_proxys函数以及IPProxy类中的update_proxys中修改参数
- 为了在你的电脑成功连接到数据库，请修改pipelines.py里MysqlPipeline类的open_spider函数以及spiders/tieba.py里
parse函数里相关参数
- 因为帖子内容里经常有emoji表情，需要设置mysql的字符集来保证不会出错。你可以参考该博客内容修改mysql 的字符集：
[MySQL中支持emoji表情的存储](https://blog.csdn.net/u013145194/article/details/51527389?utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control)
- 在项目目录下，使用`scrapy crawl tieba`运行爬虫