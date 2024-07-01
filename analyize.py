import os
from warcio.archiveiterator import ArchiveIterator
import gzip
from PIL import Image
import io
from bs4 import BeautifulSoup
import html2text

def check_files_for_string(directory, search_string):
    res = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if search_string in file:
                res += 1
    return res

def create_html(file_name, body_content):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(f"{body_content}")
    file.close()

def process(folder_path):
    other = 0
    hm = 0
    for fi in os.listdir(folder_path):
        with gzip.open(folder_path + fi, 'rb') as f:
            for record in ArchiveIterator(f, arc2warc=True):
                # if str(record.http_headers.get_header('Content-Type')) not in {'text/html', 'application/pdf', "image/png", "image/jpeg"} :
                #     print(str(record.http_headers.get_header('Content-Type')))
                if record.rec_type == 'response':
                    content_type = str(record.http_headers.get_header('Content-Type'))
                    content = record.content_stream().read()  # 二进制数据读取出来的文本数据是pdf[:4] == b'%PDF'
                    uri = record.rec_headers.get_header('WARC-Target-URI')
                    name = uri.split("?")[0].split("/")[-1]
                    if "text/html" in content_type:  # text/html; charset=utf-8
                        cnt = check_files_for_string('pdf/', name)
                        if cnt > 0:
                            name = name + "-" + str(cnt)
                        html = content.decode('utf-8')
                        create_html('html/' + name + '.html', html.replace('\n', ''))

                        soup = BeautifulSoup(html, 'html.parser')
                        h = html2text.HTML2Text()
                        h.ignore_links = False  # 保留链接
                        markdown_text = h.handle(str(soup))
                        markdown = "md/" + name + ".md"
                        with open(markdown, 'w', encoding='utf-8') as mf:
                            mf.write(markdown_text)

                        hm += 1
                    elif "application/pdf" in content_type:  # application/pdf; charset=utf-8
                        cnt = check_files_for_string('pdf/', name)
                        if cnt > 0 :
                            name = name + "-" + str(cnt)
                        file_name = 'pdf/' + name + ".pdf"
                        with open(file_name, 'wb') as file:
                            file.write(content)
                        file.close()
                    elif "image/png" in content_type:
                        if len(content) > 0:
                            image = Image.open(io.BytesIO(content))
                            name = "image/" + "image" + str(hm) + ".png"
                            image.save(name)
                    elif "image/jpeg" in content_type:
                        if len(content) > 0:
                            image = Image.open(io.BytesIO(content))
                            name = "image/" + "picture" + str(hm) + ".jpeg"
                            image.save(name)
                    else:
                        print(content_type)
                        other += 1
        f.close()
    print(other)
    print(hm)


if __name__ == "__main__":
    process('./data/')
