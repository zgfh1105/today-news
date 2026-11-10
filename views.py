# -*- coding: utf-8 -*-

# @Date    : 2018-12-17
# @Author  : Peng Shiyu


import time
import os
import hmac

from flask import render_template, request, jsonify
from playhouse.shortcuts import model_to_dict

from models import ArticleModel
from spiders import toutiao_spider, weixin_spider, segmentfault_spider


def index():
    page = int(request.args.get("page", "1"))
    tag = request.args.get("tag", "")

    # 分页控制
    if page < 1:
        page = 1

    # 标签查询
    if tag:
        rows = (ArticleModel
                .filter(ArticleModel.tag == tag)
                .order_by(-ArticleModel.publish_time)
                .paginate(page))
    else:
        rows = (ArticleModel
                .select()
                .order_by(-ArticleModel.publish_time)
                .paginate(page))

    return render_template("toutiao.html", rows=rows, page=page, tag=tag)


def crawl():
    # 爬虫触发接口必须配置独立令牌；未配置时默认关闭，避免公网匿名触发。
    expected_token = os.environ.get("CRAWL_API_TOKEN", "")
    if not expected_token:
        return jsonify({"error": "crawl endpoint is disabled: configure CRAWL_API_TOKEN"}), 503

    # 从 Authorization 请求头读取 Bearer Token，不接受 URL 查询参数传递密钥。
    authorization = request.headers.get("Authorization", "")
    provided_token = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
    # 使用恒定时间比较，避免普通字符串比较产生的时序侧信道。
    if not provided_token or not hmac.compare_digest(provided_token, expected_token):
        return jsonify({"error": "unauthorized"}), 401

    start_time = time.time()
    # toutiao_count = toutiao_spider.crawl()
    # weixin_count = weixin_spider.crawl()
    segmentfault_count = segmentfault_spider.crawl()

    time_span = int(time.time() - start_time)
    return jsonify({
        # "toutiao_count": toutiao_count,
        # "weixin_count": weixin_count,
        "segmentfault_count": segmentfault_count,
        "time_span": time_span
    })
