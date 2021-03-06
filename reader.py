# -*- coding:gb2312 -*-

# import requests
import urllib2
import xlsxwriter
import sys
import time
from bs4 import BeautifulSoup

# config char set
reload(sys)
sys.setdefaultencoding('utf-8')

# basic parameters of information
fileName = raw_input("Please enter the file name which you wanna store your data:")
while fileName is None:
    fileName = raw_input("Please enter the name of file:")

itemNumber = raw_input("Please enter the total number of items: ")
while itemNumber is None:
    itemNumber = raw_input("Please enter the total number of items: ")

# url = raw_input("Please copy the url from the top of you browser and put it here:")
# while url is None:
#     url = raw_input("Please copy the url from the top of you browser and put it here:")

aName = raw_input("Please input the applicant's name: ")
while aName is None:
    aName = raw_input("Please input the applicant's name: ")

# Create a workbook and add a worksheet.
# workbook = xlsxwriter.Workbook("./Desktop/" + fileName + ".xlsx")
workbook = xlsxwriter.Workbook("/Users/JiahengYu/Desktop/" + fileName + ".xlsx")
worksheet = workbook.add_worksheet()

# basic configurations
detailsPageUrl = 'http://cpquery.sipo.gov.cn/txnQueryBibliographicData.do?select-key:gonggaobj=1&select-key:backPage=http%3A%2F%2Fcpquery.sipo.gov.cn%2FtxnQueryOrdinaryPatents.do%3Fselect-key%3Ashenqingh%3D%26select-key%3Azhuanlimc%3D%26select-key%3Ashenqingrxm%3D%25E5%258F%25B0%25E5%25B7%259E%25E9%25A3%259E%25E8%25B7%2583%25E5%258F%258C%25E6%2598%259F%25E6%2588%2590%25E8%25A1%25A3%25E6%259C%25BA%25E6%25A2%25B0%25E6%259C%2589%25E9%2599%2590%25E5%2585%25AC%25E5%258F%25B8%26select-key%3Azhuanlilx%3D%26select-key%3Ashenqingr_from%3D%26select-key%3Ashenqingr_to%3D%26verycode%3D10%26inner-flag%3Aopen-type%3Dwindow%26inner-flag%3Aflowno%3D1508094648248&inner-flag:open-type=window&inner-flag:flowno=1508094657495&select-key:shenqingh='
searchUrl = 'http://cpquery.sipo.gov.cn//txnQueryOrdinaryPatents.do?select-key%3Ashenqingh=&select-key%3Azhuanlimc=&select-key%3Azhuanlilx=&select-key%3Ashenqingr_from=&select-key%3Ashenqingr_to=&very-code=&captchaNo=&fanyeflag=1&verycode=fanye'

# http://cpquery.sipo.gov.cn//txnQueryOrdinaryPatents.do?select-key%3Ashenqingh=&select-key%3Azhuanlimc=&select-key%3Ashenqingrxm=%E5%8F%B0%E5%B7%9E%E9%A3%9E%E8%B7%83%E5%8F%8C%E6%98%9F%E6%88%90%E8%A1%A3%E6%9C%BA%E6%A2%B0%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&select-key%3Azhuanlilx=&select-key%3Ashenqingr_from=&select-key%3Ashenqingr_to=&very-code=&captchaNo=&fanyeflag=1&verycode=fanye&attribute-node:record_start-row=1&attribute-node:record_page-row=10&#anchor

numberOfFinishedTask = 0


def decrypt(key):
    b4 = 0
    st = ''
    for i in range(0, len(key), 2):
        if (b4 > 255):
            b4 = 0
        c = int(key[i: i + 2], 16) ^ b4
        b4 += 1
        st += chr(c)
    return st


# change the url input in order to get the item from the very begining
def changeUrl(searchUrl, itemNumber, aName):
    # get all items on the first page
    # if url.find('record_page-row') > -1:
    #     url = url[0: url.index('record_page-row')] + 'record_page-row=' + itemNumber
    # else:
    url = searchUrl + '&attribute-node:record_start-row=1&attribute-node:record_page-row=' + itemNumber + '&select-key%3Ashenqingrxm=' + aName + '#anchor';
    return url


# get the item list, which is the search page
def requestWholePage(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cookie': 'language=zh; JSESSIONID=07a3e9d8f4f0e55b25f89b04eb4d; bg6149=8|WlY0P|WlYmZ',
        'Host': 'cpquery.sipo.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    request = urllib2.Request(url, headers=headers)
    return urllib2.urlopen(url).read()

# 沈阳拓荆科技有限公司
# get the patent numbers from item list page
def getPatentNumberForEachPage(wholePage):
    patentTags = BeautifulSoup(wholePage, "html.parser").find_all("a", class_='content-shenqingh')
    patentNumbers = list(map(lambda patent: str(BeautifulSoup(str(patent), "html.parser").find("a").text), patentTags))
    return patentNumbers


# the decryption key lies at the very end of the html page
def getDecryptionKey(wholePage):
    return wholePage.find_all("span")[-1].get('id')


# step into details page for each patent number given
def getDetailsOfPatent(patentNumber):
    print('Trying to get details of ' + str(patentNumber))
    headers = {
        'Cookie': 'language=zh; JSESSIONID=07a3e9d8f4f0e55b25f89b04eb4d; bg6149=8|WlYr5|WlYmZ',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Upgrade-Insecure-Requests': '1',
        'Host': 'cpquery.sipo.gov.cn',
        'Referer': 'http://cpquery.sipo.gov.cn/txnQueryOrdinaryPatents.do?select-key:shenqingh=&select-key:zhuanlimc=&select-key:shenqingrxm=%E6%B2%88%E9%98%B3%E6%8B%93%E8%8D%86%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&select-key:zhuanlilx=&select-key:shenqingr_from=&select-key:shenqingr_to=&verycode=0&inner-flag:open-type=window&inner-flag:flowno=1515596843806',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    request = urllib2.Request(detailsPageUrl + patentNumber, headers=headers)
    while True:
        try:
            response = urllib2.urlopen(request)

            pageInfo = BeautifulSoup(response.read(), "html.parser")

            decryptionKey = getDecryptionKey(pageInfo)
            decryptedKey = decrypt(decryptionKey)

            # get patentNumber
            # patentNumber

            # get caseStatus
            spanCollection = pageInfo.find("span", {"name": 'record_zlx:anjianywzt'}).findChildren()
            caseStatus = getContent(decryptedKey, spanCollection)

            # get applicationDate
            spanCollection = pageInfo.find("span", {"name": 'record_zlx:shenqingr'}).findChildren()
            applicationDate = getContent(decryptedKey, spanCollection)

            # get patentName
            spanCollection = pageInfo.find("span", {"name": 'record_zlx:zhuanlimc'}).findChildren()
            patentName = getContent(decryptedKey, spanCollection)

            # get category number
            spanCollection = pageInfo.find("span", {"name": 'record_zlx:zhufenlh'}).findChildren()
            categoryNumber = getContent(decryptedKey, spanCollection)

            # get inventor
            spanCollection = pageInfo.find("span", {"name": 'record_fmr:famingrxm'}).findChildren()
            inventor = getContent(decryptedKey, spanCollection)

            # get Applicant
            spanCollection = pageInfo.find("span", {"name": 'record_sqr:shenqingrxm'}).findChildren()
            applicant = getContent(decryptedKey, spanCollection)

            global numberOfFinishedTask
            numberOfFinishedTask += 1

            print(
                'Finish getting details of ' + str(patentNumber) + " Progress: " + str(
                    numberOfFinishedTask) + "/" + str(
                    totalNumberOfTask))

            if response.getcode() == 200:
                break
        except Exception:
            print('retry in 2 secs')
            time.sleep(2)

    return [
        patentNumber,
        patentName,
        applicant,
        inventor,
        caseStatus,
        categoryNumber,
        applicationDate
    ]


# decrypt content
def getContent(decryptedKey, spanCollections):
    result = ''
    for child in spanCollections:
        try:
            if decryptedKey.find(child.get('id')) > -1:
                result += child.text
        except:
            print decryptedKey
            print spanCollections
    return result


# write to excel
def wirteToExcel(result):
    # create ttile
    row = 0
    col = 0
    worksheet.write(row, col, 'one')
    worksheet.write(row, col + 1, 'two')
    worksheet.write(row, col + 2, 'three')
    worksheet.write(row, col + 3, 'four')
    worksheet.write(row, col + 4, 'five')
    worksheet.write(row, col + 5, 'six')
    worksheet.write(row, col + 6, 'seven')

    row += 1

    for item in result:
        worksheet.write(row, col, item[0])
        worksheet.write(row, col + 1, item[1])
        worksheet.write(row, col + 2, item[2])
        worksheet.write(row, col + 3, item[3])
        worksheet.write(row, col + 4, item[4])
        worksheet.write(row, col + 5, item[5])
        worksheet.write(row, col + 6, item[6])
        row += 1

    workbook.close()


newUlr = changeUrl(searchUrl, itemNumber, aName)
print newUlr
wholePage = requestWholePage(newUlr)
print('The whole page has been obtained')
patentNumbers = getPatentNumberForEachPage(wholePage)
totalNumberOfTask = len(patentNumbers)
print(str(len(patentNumbers)) + " has been obtained")
result = list(map(lambda number: getDetailsOfPatent(number), patentNumbers))
if result is not None or len(result) > 0:
    wirteToExcel(result)
else:
    print "Nothing has been found"
print "Finished"


# http://cpquery.sipo.gov.cn//txnQueryOrdinaryPatents.do?select-key%3Ashenqingh=&select-key%3Azhuanlimc=&select-key%3Ashenqingrxm=%E5%8F%B0%E5%B7%9E%E9%A3%9E%E8%B7%83%E5%8F%8C%E6%98%9F%E6%88%90%E8%A1%A3%E6%9C%BA%E6%A2%B0%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&select-key%3Azhuanlilx=&select-key%3Ashenqingr_from=&select-key%3Ashenqingr_to=&very-code=&captchaNo=&fanyeflag=1&verycode=fanye&attribute-node:record_start-row=11&attribute-node:record_page-row=10&#anchor
