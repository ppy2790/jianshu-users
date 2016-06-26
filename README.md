> 这里没有用到rule进行抓取



实现一个爬虫的关键，我理解下来有两点：

一是url分析，就是从哪里进入，经过哪些路径（列表页，分页），新增url在哪里添加，这些关系到一个数据完整的链路。

二是页面源代码分析，解析出需要的数据（包括一个完整的数据在哪几个页面上获取）。主要弄清文档结构，数据的选取点放在哪里。

搞清楚这两个要点后，实现一个爬虫的功能不难，无论是采用Scrapy框架，还是用Python+正则，或BeautifulSoup的方式。

下面尝试从一个案例来分析，使用Scrapy框架如何规划url，最终拿到要解析的数据。

###先从要抓取的数据和最终页面来分析URL
简书的用户首页的url是这样的http://www.jianshu.com/users/54b5900965ea/，即/users+ 用户ID，但是不同类型的用户看到用户首页是不一样的，同样是/users/userId进来的，发表过文章的用户的首页指向的是http://www.jianshu.com/users/54b5900965ea/latest_articles 即最新文章页面（latest_articles）, 没发表文章的用户（包括点赞、评论、粉）指向的页面是http://www.jianshu.com/users/useridxxxx/timeline，即最新动态页面（timeline）

这两种页面上都有我们所需要的信息，左边都是个人信息+发表文章汇总数据，互动数据。如果我们要获得用户的注册时间，一共发表多少评论（这算一个用户活跃数据），这两个数据只能在timeline(最新动态)页面上获取。

为什么要分析url，是因为爬虫要解析页面，如果同一个入口，对应两个不同的页面，程序在运行时，就也不能决定下一步怎么走，增加了程序编写的复杂度。所以我在抓取用户数据时，把获取用户数据的页面定为timeline页。注意，要获取用户注册时间，在timeline的最后一页。所以timeline的最后一页，我们开始解析数据。

评论数就比较麻烦，需要在每一页上进行统计，在timeline最后一页汇总，提交item。


###如何拿到分页的URL？
基本上分页有两种处理方式：
1）知道总记录数，每页记录条数，那就能很快构造一个url，一个循环就能解决，也能快速定位到最后一页获取数据。

获取一个特征用户的粉丝url (之后用于构造用户的最新动态页timeline)，就是采用的这种方法。

2）无法知道总记录数，页面和源代码中均没有。一般这种分析是通过一个“加载更多”按钮来提交下一页的url，url参数中常有maxid和其他看似奇怪的参数，不是通常的page=n这种。

在简书首书的热门文章分页，用户的最新动态分页，都是这种方式。方法就是解析出分页对应的url, 再进行递归调用即可。

怎样知道是哪一种分页方式，用chrome的元素审查功能，打开network加载下一页时查看url，并结合源代码进行分析，即可搞定。


分析url

反查源代码
分析一下爬虫运行时URL规划
即如何从爬虫入口URL到解析数据的页面。

1、待爬取的URL放在start_urls列表中，爬虫启动后parse()会依次从该列表中处理每一个url。列表中放的是大咖的粉丝页url，即 /users/useridxxx/followers

    # 获取粉丝分页信息  进口url followers, 出口followers分页url
    def parse(self, response):
        selector = Selector(response)

        fnum = selector.xpath('/html/body/div[4]/div[2]/ul/li[3]/a/text()').extract()[0]

        fnum = filter(str.isdigit, str(fnum))

        pages = int(fnum) / 9 + 1
        t = int(time.time())

        for i in range(1, pages + 1):
            nurl = response.url + '?_' + str(t) + '&page=' + str(i)

            yield  Request(nurl,callback=self.parse_user_url)
这时要进行分页处理，即拿到粉丝分页的所有url，接下来从这个url解析出用户的首页。转去调用 parse_url()方法。

2、parser_url()方法，入口的url是分页的follower页面，目标是解析数据后拿到用户url， 再构造出最态动态url, 出口的url是/users/usridxxx/timeline，再去调用parse_user_detail()方法。

    #获取用户timeline  进口url followers ,出口url timeline
    def parse_user_url(self,response):

        selector = Selector(response)

        users = selector.xpath('//ul[@class="users"]/li/a/@href').extract()

        for user in users:
            userurl = 'http://www.jianshu.com' + user + '/timeline'
            yield Request(userurl, callback=self.parse_user_detail)
3、parse_user_detail()完成最终的数据解析。
注意，此时timeline需要分页处理，这里也需要递归调用。还涉及到Request之间传递参数，最终一个用户完整的信息是在多个页面获取的。

               yield Request(url, meta={'comments':comment},callback=self.parse_user_detail)
至此，一个完整爬虫url分析完毕，代码实现基本可以一气呵成。
