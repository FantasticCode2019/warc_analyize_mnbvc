在warc数据流中，可以使用自带的read函数来读取数据流中的数据。

```python
import requests
from warcio.archiveiterator import ArchiveIterator

def print_records(url):
    resp = requests.get(url, stream=True)

    for record in ArchiveIterator(resp.raw, arc2warc=True):
        if record.rec_type == 'warcinfo':
            print(record.raw_stream.read())

        elif record.rec_type == 'response':
            if record.http_headers.get_header('Content-Type') == 'text/html':
                print(record.rec_headers.get_header('WARC-Target-URI'))
                print(record.content_stream().read())
                print('')

# WARC
print_records('https://archive.org/download/ExampleArcAndWarcFiles/IAH-20080430204825-00000-blackbook.warc.gz')


# ARC with arc2warc
print_records('https://archive.org/download/ExampleArcAndWarcFiles/IAH-20080430204825-00000-blackbook.arc.gz')
```

为了区分从warc文件中读取的数据类型，可以根据`record.rec_type`和`record.http_headers.get_header('Content-Type')`它的值来判断。

`record.rec_type`的值为`response`；
`record.http_headers.get_header('Content-Type')`值有以下几点：
+ 为`text/html; charset=utf-8`时，该数据是一个解析html格式类型的数据；
+ 为`application/pdf; charset=utf-8`时，该数据是一个pdf文件；
+ 为`image/jpeg`时，该数据是一个图片文件；
+ 为`application/json; charset=utf-8`时，该数据是一个json文件；
+ 为`application/xml; charset=utf-8`时，该数据是一个xml文件；
+ 为`text/plain; charset=utf-8`时，该数据是一个普通文本文件；
+ 为`application/javascript; charset=utf-8`时，该数据是一个js文件；

warc的功能是将网络数据保存到一个文件中，方便数据的解析和存储。数据转化为二进制的形式进行存储，注意读取数据为pdf类型时，read()函数返回的字符串前缀有`b'PDF%'`.

另外，有如下写入数据的方法：
参考链接：https://github.com/webrecorder/warcio
```python
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders

import requests

with open('example.warc.gz', 'wb') as output:
    writer = WARCWriter(output, gzip=True)

    resp = requests.get('http://example.com/',
                        headers={'Accept-Encoding': 'identity'},
                        stream=True)

    # get raw headers from urllib3
    headers_list = resp.raw.headers.items()

    http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')

    record = writer.create_warc_record('http://example.com/', 'response',
                                        payload=resp.raw,
                                        http_headers=http_headers)

    writer.write_record(record)
```
现对html数据进行过滤和筛选：
先把所有的html数据转化为markdown格式，然后再对其进行筛选。
对整个数据采用分类的方法进行过滤：
训练了一个逻辑回归的线性分类器，使用的特征是spark里的HashingTF，正样本是WebText, Wikiedia, and our web books corpus；
负样本是unfiltered Common Crawl原始的Common Crawl文本（这里指的是带筛选的html文本 or markdown文本）。

`analyize.py`可以把warc数据分成html、image、markdwon、pdf这四种格式的数据
