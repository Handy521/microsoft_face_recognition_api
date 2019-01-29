#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 14:59:06 2019

@author: shinong
"""

import requests
import json
import time
import http
import urllib

class FaceRecognizer(object):
    
    def __init__(self,personGroupId):
        self.subscription_key='68e05b40bd014e379942ea072d9650aXX'
        self.http_uri='https://chinaeast2.api.cognitive.azure.cn'
        self.conn=http.client.HTTPSConnection('chinaeast2.api.cognitive.azure.cn')
        self.Request_POST='POST'
        self.headers_josn={
                'Content-Type': 'application/josn',
                'Ocp-Apim-Subscription-Key': self.subscription_key,}                
        self.headers_octet={
                'Content-Type': 'application/octet-stream',
                'Ocp-Apim-Subscription-Key': self.subscription_key,}
        self.params=  urllib.parse.urlencode({ 
                 })  
        self.personGroupId=personGroupId  
    #识别detect脸
    def selectLocalFace(self,image_path):
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
        f=open(image_path,"rb").read()
        body = {'url': image_path}
        response = requests.request(self.Request_POST, self.http_uri + '/face/v1.0/detect', json=body, \
                                    data=f, headers=self.headers_octet, params=params)
        parsed = json.loads(response.text) 
        facesId=parsed[0].get('faceId')
        return facesId

    #创建人员组
    #personGroupId为人员组ID,name为人员组名称,userData为用户提供的附加到人员组的数据
    def createGroup(self,name,userData):        
        Request='PUT'
        body=("{"+"'name':'"+name+"',"+"'userData':'"+userData+"'}")
        self.conn.request(Request,"/face/v1.0/persongroups/%s" % self.personGroupId,body,self.headers_octet)
        response=self.conn.getresponse()
        print(response.reason)
        if response.reason=="OK":
            print("人员组创建成功")
        else:
            print("人员组创建失败")
        self.conn.close()
        
    #创建一个人(名字可以相同，但是返回的ID是唯一需要记住)
    #personGroupId已创建好的人员组ID，personName创建的人员名称
    #返回的personId唯一，需要记住
    def addPersonNa(self,person):
    
        headers={
        #     'Content-Type': 'application/josn',   #wrong_media type,must delete
            'Ocp-Apim-Subscription-Key': self.subscription_key,}      
        body=("{"+"'name':'"+person+"',"+"'userData':''}")
        self.conn.request('POST',"/face/v1.0/persongroups/%s/persons?"%self.personGroupId,body,headers)
        response = self.conn.getresponse()
        data = response.read()
        print(data)
        s1=str(data)
        s2=s1[2:-1]
        s3=eval(s2)
        s4=s3["personId"]
        return s4
        self.conn.close()
    
    def delete_person(self,personId):
        
        personGroupId='shinong_group'
        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': self.subscription_key,
                            }
        userData=' '
        body=("{"+"'name':'"+'person'+"',"+"'userData':'"+userData+"'}")
        conn=http.client.HTTPSConnection('chinaeast2.api.cognitive.azure.cn')
        conn.request("DELETE", "/face/v1.0/persongroups/%s/persons/%s?" % (personGroupId,personId),\
                     body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
        
    #向人员中添加人脸(返回的人脸ID是持久的：用作于人脸-识别和人员-删除人脸)
    #personGroupId已创建好的人员组ID,personId已创建好的人员ID,imagesUrl本地图片路径
    def addPersonFace(self,personId,image_path):        
        #上传本地图片
        f=open(image_path,"rb")
        body = {'url': image_path}
        response = requests.request(
                self.Request_POST, self.http_uri + '/face/v1.0/persongroups/%s/persons/%s/persistedFaces?%s'  \
                % (self.personGroupId,personId,self.params), json=body, data=f, headers=self.headers_octet, params=self.params)
        print ('Response:')
        parsed = json.loads(response.text)
        print(parsed) 
        time.sleep(0.2)
        
    def train_person(self):
        """
        after add face,begin train 
        """
        self.conn.request(self.Request_POST, "/face/v1.0/persongroups/%s/train?%s"  \
                     % (self.personGroupId,self.params), "{body}", self.headers_octet)
        response = self.conn.getresponse()
        data = response.read()
        print(data)
        self.conn.close()
        
    #查询训练人员组状态
    def seltrainGroup(self):

        Request="GET"
        self.conn.request(Request, "/face/v1.0/persongroups/%s/training?%s" \
                     % (self.personGroupId,self.params), "{body}", self.headers_octet)
        response = self.conn.getresponse()
        data = response.read()
        print(data)
        self.conn.close()

    #检测相似度
    def identifyFace(self,faceIds,maxNumOfCandidatesReturned,confidenceThreshold):
    
        headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': self.subscription_key,}      
        stra='{"personGroupId":"'
        strb='","faceIds":["'
        strc='"],"maxNumOfCandidatesReturned":'
        strd=',"confidenceThreshold": '
        stre='}' 
        body='%s%s%s%s%s%s%s%s%s'%(stra,self.personGroupId,strb,faceIds,strc,maxNumOfCandidatesReturned,strd,confidenceThreshold,stre)
        print(body)
        self.conn.request("POST", "/face/v1.0/identify?%s" % self.params, body, headers=headers)#headers global variable invalid
        response = self.conn.getresponse() 
        data = response.read()
        data=data.decode()
        data=data.strip('[]') 
        data=eval(data)
        candidates=data["candidates"]
        print(candidates[0]["personId"])
        print(candidates[0]["confidence"])
        self.conn.close()
        
    def identifyFace2(self,faceIds):
        #检测相似度(second method)
        headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': self.subscription_key,}    
        API_URL=self.http_uri+"/face/v1.0/identify"
        body={
              "personGroupId":self.personGroupId,
              "faceIds":[faceIds],
              "maxNumOfCandidatesReturned": 1,
              "confidenceThreshold": 0.5
              }
        print(body)
        response=requests.request(self.Request_POST,API_URL,params=self.params,data=None,
                                  json=body,headers=headers)
        parsed=json.loads(response.text)
        print(parsed)
        
    def faceId_convert_name(personId):
        
        name_dict={"a83b8f8f-804f-4e67-aedc-f0c6ec9fe648":'handy',
                   "d69ddf9d-2415-43e2-8c8f-ee9d66cd3a1a":'fy',
                   "b0e7f2fa-445f-44c9-accc-f6adecc05144":'yan'}
        print(name_dict[personId])
        
if __name__ == '__main__' :

    recongizer=FaceRecognizer('shinong_group')
#    recongizer.addPersonNa('yan')
    image_path='115168449.jpg'
#    recongizer.addPersonFace("b0e7f2fa-445f-44c9-accc-f6adecc05144",image_path)
#    recongizer.train_person()
#    recongizer.seltrainGroup()
    faceid=recongizer.selectLocalFace(image_path)
    recongizer.identifyFace2(faceid)