#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 20:59:40 2019

@author: shinong
"""
import os
import requests
import cv2
import base64
import json
import shutil
import numpy as np
from pprint import pprint
import time
import http
import urllib
subscription_key='68e05b40bd014e379942ea072d9650a6X'
http_uri = 'https://chinaeast2.api.cognitive.azure.cn'
uri_base = 'chinaeast2.api.cognitive.azure.cn'
#识别detect脸
def selectLocalFace(imagesUrl):
#    try:
    Request='POST'
    #Content_Type1传递类型
    Content_Type1='application/octet-stream'
#    Content_Type1='application/josn'
    headers = {
     'Content-Type': Content_Type1,
     'Ocp-Apim-Subscription-Key': subscription_key,
        }
    #设定是否返回FaceID
    returnFaceId='true'
    #设定是否返回详细的面部细节位置信息（包括鼻子、眼睛、嘴等）
    returnFaceLandmarks='false'
    #设定进行面部智能分析
    #可选：age, gender, smile intensity, facial hair, head pose, glasses, emotion, hair, makeup, occlusion, accessories, blur, exposure and noise
    returnFaceAttributes='age,gender,facialHair,glasses,hair'
    params = { 'returnFaceId': returnFaceId,
              'returnFaceLandmarks': returnFaceLandmarks,
                'returnFaceAttributes':returnFaceAttributes,}
    #上传本地图片
    f=open(imagesUrl,"rb").read()
    body = {'url': imagesUrl}
    response = requests.request(Request, http_uri + '/face/v1.0/detect', json=body, data=f, headers=headers, params=params)
    print ('Response:',response)
    parsed = json.loads(response.text)
    print(parsed) 
#    facenums=0;
    faceAll=[]
#    #提取出faceId和人脸的矩形框定位
#    for a in parsed:
#        for b in a:
#            if b=="faceId":
#                faceId=a[b]
#                print(faceId)
#            if b=="faceRectangle":
#                top=a[b]["top"]
#                left=a[b]["left"]
#                width=a[b]["width"]
#                height=a[b]["height"] 
#            if b=="faceAttributes":
#                gender=a[b]["gender"]
#                age=a[b]["age"]
#        imagesFace=[faceId,left,top,width,height,gender,age]
#        faceAll.append(imagesFace)
#    print(faceAll)
    return faceAll
#    except Exception as e:
#        print("Error")
#        print(e)
#        return -1
#创建人员组
#personGroupId为人员组ID,name为人员组名称,userData为用户提供的附加到人员组的数据
def createGroup(personGroupId,name,userData):
    try:
        headers = {
     'Ocp-Apim-Subscription-Key': subscription_key,
        }
        conn = http.client.HTTPSConnection(uri_base)
        Request='PUT'
        #personGroupId=input("输入创建人员组ID(英文)：")
        #name=input("人员组名称：")
        #userData=input("附加到人员组用户提供的数据(可选)：")
        body=("{"+"'name':'"+name+"',"+"'userData':'"+userData+"'}")
        conn.request(Request,"/face/v1.0/persongroups/%s" % personGroupId,body,headers)
        response=conn.getresponse()
        print(response.reason)
        if response.reason=="OK":
            print("人员组创建成功")
        else:
            print("人员组创建失败")
        conn.close()
    except Exception as e:
        print("Error")
        print(e)   
#创建一个人(名字可以相同，但是返回的ID是唯一需要记住)
#personGroupId已创建好的人员组ID，personName创建的人员名称
#返回的personId唯一，需要记住
def addPersonNa(personGroupId,personName):
    try:
        headers = {
         'Content-Type': 'application/json',
         'Ocp-Apim-Subscription-Key': subscription_key,
        }
        userData="its_ok"
        Request="POST" 
        body=("{"+"'name':'"+personName+"',"+"'userData':'"+userData+"'}")
        conn = http.client.HTTPSConnection(uri_base)
        conn.request(Request,"/face/v1.0/persongroups/%s/persons?" % personGroupId,body,headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        s1=str(data)
        s2=s1[2:-1]
        s3=eval(s2)
        s4=s3["personId"]
        return s4
        conn.close()
    except Exception as e:
        print("Error")
        print(e)
#向人员中添加人脸(返回的人脸ID是持久的：用作于人脸-识别和人员-删除人脸)
#personGroupId已创建好的人员组ID,personsId已创建好的人员ID,imagesUrl本地图片路径
def addPersonFace(personGroupId,personsId,imagesUrl):
    try:
        Request='POST'
        #Content_Type1传递类型
        Content_Type1='application/octet-stream'
        headers = {
         'Content-Type': Content_Type1,
         'Ocp-Apim-Subscription-Key': subscription_key,
            }
        params = urllib.parse.urlencode({
        # Request parameters
        'userData': '',
        'targetFace': '',
        })
        #上传本地图片
        f=open(imagesUrl,"rb")
        body = {'url': imagesUrl}
        response = requests.request(Request, http_uri + '/face/v1.0/persongroups/%s/persons/%s/persistedFaces?%s'  \
                                    % (personGroupId,personsId,params), json=body, data=f, headers=headers, params=params)
        print ('Response:')
        parsed = json.loads(response.text)
        print(parsed) 
        facenums=0;
        time.sleep(0.2)
    except Exception as e:
        print("Error")
        print(e)
def train_person(personGroupId):
    Content_Type1='application/octet-stream'
    headers = {
         'Content-Type': Content_Type1,
         'Ocp-Apim-Subscription-Key': subscription_key,
            }
    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection(uri_base)
        conn.request("POST", "/face/v1.0/persongroups/%s/train?%s" % (personGroupId,params), "{body}", headers)
        response = conn.getresponse()
        data = response.read()
#        parsed = json.loads(response.text)
#        print(parsed) 
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
#查询训练人员组状态
def seltrainGroup(personGroupId):
    try:
        headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': subscription_key,
        }
    
        params = urllib.parse.urlencode({
        })
        Request="GET"
        conn = http.client.HTTPSConnection(uri_base)
        conn.request(Request, "/face/v1.0/persongroups/%s/training?%s" % (personGroupId,params), "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("Error")
        print(e)
#检测相似度
def identifyFace(personGroupId,faceIds,maxNumOfCandidatesReturned,confidenceThreshold):
    try:
        #maxNumOfCandidatesReturned=1
        #confidenceThreshold=0.5
        Content_Type1='application/octet-stream'
        Content_Type2='application/json'
        headers = {
        # Request headers
        'Content-Type': Content_Type2,
        'Ocp-Apim-Subscription-Key': subscription_key,
        }
        params = urllib.parse.urlencode({
                                        })
        stra='{"personGroupId":"'
        strb='","faceIds":["'
        strc='"],"maxNumOfCandidatesReturned":'
        strd=',"confidenceThreshold": '
        stre='}' 
        body='%s%s%s%s%s%s%s%s%s'%(stra,personGroupId,strb,faceIds,strc,maxNumOfCandidatesReturned,strd,confidenceThreshold,stre)
        print(body)
        conn = http.client.HTTPSConnection(uri_base)
        conn.request("POST", "/face/v1.0/identify?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        data=data.decode()
        data=data.strip('[]') 
        data=eval(data)
        faceIdr=data["faceId"]
        candidates=data["candidates"]
        print(candidates[0]["personId"])
        print(candidates[0]["confidence"])
        conn.close()
    except Exception as e:
        print('Error:')
        print(e)
#selectLocalFace('/home/shinong/Downloads/1187562263.jpg')
#createGroup('shinong_group','group1','its_ok')
#s4=addPersonNa('shinong_group','handy')
image_path='/home/shinong/Desktop/Cognitive-Face-Windows/Data/PersonGroup/Family1-Son/Family1-Son1.jpg'
#image_path='/home/shinong/Desktop/Cognitive-Face-Windows/Data/PersonGroup/Family1-Son/Family1-Son2.jpg'
#image_path='/home/shinong/Desktop/Cognitive-Face-Windows/Data/PersonGroup/Family1-Son/Family1-Son3.jpg'
#addPersonFace('shinong_group',"a83b8f8f-804f-4e67-aedc-f0c6ec9fe648",image_path)
#train_person('shinong_group')
   
#selectLocalFace(image_path)
#seltrainGroup('shinong_group')
identifyFace('shinong_group','2d54298a-177e-4450-bc7a-e491cc05b238',1,0.5)
