# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:22:27 2021

@author: XiujuanCaoer

@Description:
    基于四个点坐标使用opencv从图片中剪裁出任意形状的四边形
    思路：
        1.计算要裁剪区域最小外接四边形的相对水平方向的旋转角度；
        2.将原图旋转该角度，以使得要裁剪的区域旋转到水平方向；
        3.将要裁剪区域的坐标做相应的转换，转换为旋转后的坐标；
        4.对该区域进行裁剪。
    
    代码参考：https://blog.csdn.net/u013250416/article/details/81104872
    
    准备：一个文件夹只包含以img_X.jpg命名的批量图片及其同样命名的txt文件。
        txt文件中包含着八个坐标值和国家以及标注，eg.2077,1293,2038,1118,2819,936,2793,1148,Korean,송승종
        八个坐标分别对应四个坐标点的x,y值，左上[x1, y1] 右上[x2, y2] 右下[x3, y3] 左下[x4, y4]
"""
import cv2
import numpy as np
import math
 
'''旋转图像并剪裁'''
def rotate(
        img,  # 图片
        pt1, pt2, pt3, pt4,
        newImagePath
):
    print (pt1,pt2,pt3,pt4)
    withRect = math.sqrt((pt4[0] - pt1[0]) ** 2 + (pt4[1] - pt1[1]) ** 2)  # 矩形框的宽度
    heightRect = math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) **2)
    print (withRect,heightRect)
    angle = math.acos((pt4[0] - pt1[0]) / withRect) * (180 / math.pi)  # 矩形框旋转角度
    print (angle)
 
    if pt4[1] > pt1[1]:
        print ("顺时针旋转")
    else:
        print ("逆时针旋转")
        angle = -angle
 
    height = img.shape[0]  # 原始图像高度
    width = img.shape[1]   # 原始图像宽度
    rotateMat = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)  # 按angle角度旋转图像
    heightNew = int(width * math.fabs(math.sin(math.radians(angle))) + height * math.fabs(math.cos(math.radians(angle))))
    widthNew = int(height * math.fabs(math.sin(math.radians(angle))) + width * math.fabs(math.cos(math.radians(angle))))
 
    rotateMat[0, 2] += (widthNew - width) / 2
    rotateMat[1, 2] += (heightNew - height) / 2
    imgRotation = cv2.warpAffine(img, rotateMat, (widthNew, heightNew), borderValue=(255, 255, 255))
 
    # 旋转后图像的四点坐标
    [[pt1[0]], [pt1[1]]] = np.dot(rotateMat, np.array([[pt1[0]], [pt1[1]], [1]]))
    [[pt3[0]], [pt3[1]]] = np.dot(rotateMat, np.array([[pt3[0]], [pt3[1]], [1]]))
    [[pt2[0]], [pt2[1]]] = np.dot(rotateMat, np.array([[pt2[0]], [pt2[1]], [1]]))
    [[pt4[0]], [pt4[1]]] = np.dot(rotateMat, np.array([[pt4[0]], [pt4[1]], [1]]))

    # 处理反转的情况
    if pt2[1] > pt4[1]:
        pt2[1],pt4[1] = pt4[1],pt2[1]
    if pt1[0] > pt3[0]:
        pt1[0],pt3[0] = pt3[0],pt1[0]
 
    imgOut = imgRotation[int(pt2[1]):int(pt4[1]), int(pt1[0]):int(pt3[0])]
#    imgOut = cv2.resize(imgOut, (280, 32), interpolation=cv2.INTER_AREA)
    if imgOut.any():
           cv2.imwrite(newImagePath, imgOut)  # 裁减得到的旋转矩形框
    else:
           print("出现空图！")
    
    return imgRotation  # rotated image
 
 
#　根据四点画原矩形
def drawRect(img,pt1,pt2,pt3,pt4,color,lineWidth):
    cv2.line(img, pt1, pt2, color, lineWidth)
    cv2.line(img, pt2, pt3, color, lineWidth)
    cv2.line(img, pt3, pt4, color, lineWidth)
    cv2.line(img, pt1, pt4, color, lineWidth)
 
#　读出文件中的坐标值
def ReadTxt(directory,txtName, imageName):
    fileTxt = txtName  # txt文件名
    getTxt = open(fileTxt, 'r', encoding='UTF-8')  # 打开txt文件
    lines = getTxt.readlines()
    length = len(lines)
    imgSrc = cv2.imread(imageName)
    
    result_file = []
    result_label = []
    for i in range(0,length):
        items = lines[i].split(',')
        if items[9].strip() != '###':  # 此处过滤掉了###即未知命名图像的切割
               pt1 = [int(items[0]), int(items[1])]
               pt4 = [int(items[6]), int(items[7])]
               pt3 = [int(items[4]), int(items[5])]
               pt2 = [int(items[2]), int(items[3])]
               
               imgRotation = rotate(imgSrc,pt1,pt2,pt3,pt4,str(i)+'_'+imageName)
               if imgRotation.any():#过滤掉空图——未得到裁剪图像的图
                      result_file.append(str(i)+'_'+imageName)
                      result_label.append(items[9].strip())
        
    return result_file, result_label

if __name__=="__main__":
    directory = "j:/data_cut/"# 记得修改你的路径
    
    fileName = []
    for num in range(1, 7):# 此处修改图片的张数,图片的命名必须是img_X
           fileName.append("img_" + str(num))
    
    
    result_files = []
    result_labels = []
    for i in fileName:
           txtName = i + '.txt'  # 每张图需要切割的四点坐标文件名
           imageName =  i + '.jpg'  # 每张图的文件名 
           result_file, result_label = ReadTxt(directory, txtName, imageName)
           result_files.extend(i for i in result_file)
           result_labels.extend(i for i in result_label)
    
    # 结果list保存的文件名，格式：文件名 注释，eg.0_img_1.jpg 얼음
    with open(directory+'/result_list.txt', 'w', encoding = 'utf-8') as openFile:
           for i in range(len(result_files)):
                  openFile.write(result_files[i])
                  openFile.write(' ')
                  openFile.write(result_labels[i])
                  openFile.write('\n')
    openFile.close()
    print(result_labels)
