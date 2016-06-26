# coding=utf-8
# -*- coding : utf-8-*-

from scrapy.spiders import CrawlSpider
from jusers.items import JusersItem
from scrapy.selector import Selector
from scrapy.http import Request
import time
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')


class UserSpider(CrawlSpider):

    name = 'juser'

    start_urls=['http://www.jianshu.com/users/1441f4ae075d/followers',
                'http://www.jianshu.com/users/8f03f4df0d30/followers',
                'http://www.jianshu.com/users/9a5983ec2ea8/followers'
                'http://www.jianshu.com/users/086567bede72/followers',
                'http://www.jianshu.com/users/yZq3ZV/followers',
                'http://www.jianshu.com/users/y3Dbcz/followers',
                'http://www.jianshu.com/users/aTFqFm/followers',
                'http://www.jianshu.com/users/e8f8f895861d/followers',
                'http://www.jianshu.com/users/d90828191ace/followers',
                'http://www.jianshu.com/users/72f7e8a56495/followers',
                'http://www.jianshu.com/users/e62e6a7af892/followers',
                'http://www.jianshu.com/users/c340386c4c96/followers',
                'http://www.jianshu.com/users/2a932b14d734/followers',
                'http://www.jianshu.com/users/0419c254f1b6/followers',
                'http://www.jianshu.com/users/3fdcc04b7bd7/followers'
                ]


    # 获取粉丝分页信息  进口url followers, 出口followers分页url
    def parse(self, response):

        item_urls = set()
        selector = Selector(response)

        fnum = selector.xpath('/html/body/div[4]/div[2]/ul/li[3]/a/text()').extract()[0]

        fnum = filter(str.isdigit, str(fnum))

        pages = int(fnum) / 9 + 1

        t = int(time.time())

        for i in range(1, pages + 1):
            nurl = response.url + '?_' + str(t) + '&page=' + str(i)

            yield  Request(nurl,callback=self.parse_user_url)


    #获取用户timeline  进url followers ,出口url timeline
    def parse_user_url(self,response):

        selector = Selector(response)

        users = selector.xpath('//ul[@class="users"]/li/a/@href').extract()

        for user in users:
            userurl = 'http://www.jianshu.com' + user + '/timeline'
            yield Request(userurl, callback=self.parse_user_last_timelinepage)


    #进来url timeline  处理数据
    def parse_user_last_timelinepage(self,response):


        selector = Selector(response)


        try:
            timelines = selector.xpath('//div[@class="timeline-list"]/ul')

            try:
                mtype = response.meta['mtype']
                last_time = response.meta['last_time']
            except:

            #if response.url.find('max_id=') == -1 :
                mtype = timelines[0].xpath('li/@class').extract()[0]
                mtype = str(mtype)
                if mtype =='comment':
                    mtype ='发表了评论'
                elif mtype =='user-update':
                    mtype ='关注或喜欢'
                elif mtype =='user-update article':
                    mtype ='发表了文章'

                last_time = selector.xpath('//div/time/text()').extract()[0]



            ###此处判断需要验证 1)字符串的判断, 2)url传递参数
            # if lastupdate == '':
            #     action = timelines[0].xpath('li/span/a/text()').extract()[0]
            #     actiontime = timelines[0].xpath('li/div[@class="meta"]/time/text()').extract()[0]
            #
            #     lastupdate = actiontime



            try:
                comment = response.meta['comments']
            except:
                comment = 0

            comms = timelines[0].xpath('li[@class="comment"]').extract()

            if len(comms)>0:
                comm = len(comms)

                comment += comm

            nextbutton = selector.xpath('//button[@class="ladda-button "]/@data-url').extract()

            if len(nextbutton) == 1:
                url = "http://www.jianshu.com"+nextbutton[0]

                yield Request(url, meta={'comments':comment,'mtype':mtype,'last_time':last_time},callback=self.parse_user_last_timelinepage)

            else:

                item = JusersItem()
                selector = Selector(response)

                userinfo = selector.xpath('//div[@class="people"]')

                nickname = userinfo[0].xpath('div[1]/h3/a/text()').extract()[0]

                #print nickname
                item['nickname'] = nickname
                item['url'] = response.url

                writeinfo = userinfo[0].xpath('div[2]/ul/li/a/b/text()').extract()

                item['subscriptions'] = int(writeinfo[0])
                item['fans'] = int(writeinfo[1])
                item['articles'] = int(writeinfo[2])
                item['words'] = int(writeinfo[3])
                item['likes'] = int(writeinfo[4])
                item['comments']=comment

                regtime = selector.xpath('//div/time/text()').extract()
                regtime= regtime[len(regtime)-1]
                item['regtime']=regtime
                item['lasttime']=last_time
                item['lastact']=mtype

                yield item

        except:

            print '-------user not exist!--------'







