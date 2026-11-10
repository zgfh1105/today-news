# -*- coding: utf-8 -*-

# @Date    : 2018-09-13
# @Author  : Peng Shiyu

from flask import Flask

import views

app = Flask(__name__)

app.add_url_rule("/", view_func=views.index)
app.add_url_rule("/crawl", view_func=views.crawl)

if __name__ == '__main__':
    app.run(debug=False)  # 生产环境关闭 Debug，避免泄露调试信息
