# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 11:38:34 2021

@author: Caoer
"""
 
import os
from PyPDF2 import PdfFileReader, PdfFileWriter
import time
 
 
# 使用os模块的walk函数，搜索出指定目录下的全部PDF文件
# 获取同一目录下的所有PDF文件的绝对路径
def getFileName(filedir):
 
    file_list = [os.path.join(root, filespath) \
                 for root, dirs, files in os.walk(filedir) \
                 for filespath in files \
                 if str(filespath).endswith('pdf')
                 ]
    return file_list if file_list else []
 
# 合并同一目录下的所有PDF文件
def MergePDF(filepath, outfile):
 
    output = PdfFileWriter()
    outputPages = 0
    pdf_fileName = getFileName(filepath)
 
    if pdf_fileName:
        for pdf_file in pdf_fileName:
            print("路径：%s" % pdf_file)
 
            # 读取源PDF文件
            input = PdfFileReader(open(pdf_file, "rb"))
 
            # 获得源PDF文件中页面总数
            pageCount = input.getNumPages()
            outputPages += pageCount
            print("页数：%d"%pageCount)
 
            # 分别将page添加到输出output中
            for iPage in range(pageCount):
                output.addPage(input.getPage(iPage))
 
        print("合并后的总页数:%d."%outputPages)
        # 写入到目标PDF文件
        outputStream = open(r"%s" % os.path.join(filepath, outfile), "wb")
        output.write(outputStream)
        outputStream.close()
        print("PDF文件合并完成！")
 
    else:
        print("没有可以合并的PDF文件！")

if __name__ == '__main__':
    time1 = time.time()
    file_dir = input("J:/0_cxj/中期/") # 存放PDF的原文件夹
    outfile = input('J:/0_cxj/中期/output.pdf') # 输出的PDF文件的名称
    MergePDF(file_dir, outfile)
    time2 = time.time()
    print('总共耗时：%s s.' %(time2 - time1) ,'保存在：%s' %file_dir)
