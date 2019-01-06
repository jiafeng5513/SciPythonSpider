MedSci爬虫
=====================
### about
1. 从[MedSci](http://www.medsci.cn/)上爬取SCI期刊的信息
2. 输入数据是ISSN,来源是中科院SCI分区表2017年版本
3. 使用百度翻译API对期刊名称进行了机器翻译
4. 能够获取期刊的英文全名,中文全名(机器翻译),年文章数,投稿难易度,初审周期,主页链接
5. `issn.csv中`是issn号码,从中科院分区表中查询到的.
6. `sci_jcr_2017.csv`原版的中科院分区表
7. `jcr-plus.xlsx`是手动整合的爬虫数据和jcr分区表,并进行了校验
8. `res.csv`是程序的输出数据,文件名在主函数里面指定,程序运行前请确定该文件存在且为空.

### build
1. python3
2. pandas,BeautifulSoup,urllib

### run
run the mySpider.py