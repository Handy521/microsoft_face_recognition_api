# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 03:48:39 2019

@author: yong2
"""

import requests
import json
import http
import urllib
import cv2

class FaceRecognizer(object):
    
    def __init__(self,personGroupId):
        self.subscription_key='68e05b40bd014e379942ea072d9650aX'
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
#        returnFaceAttributes='age,gender,facialHair,glasses,hair'
        params = { 'returnFaceId': returnFaceId,
                  'returnFaceLandmarks': returnFaceLandmarks,
                    'returnFaceAttributes':'age',}
        #上传本地图片
        f=open(image_path,"rb").read()
#        img_str = base64.b64encode(image_path).decode() 
        body = {'url': image_path}
        #0.4s调用一次，不能实时
        response = requests.request(self.Request_POST, self.http_uri + '/face/v1.0/detect', json=body, \
                                    data=f, headers=self.headers_octet, params=params)
        parsed = json.loads(response.text) 
        print(parsed)
        rectangle,Id,age=[],[],[]
        for i,index in enumerate(parsed):
            
            facesId=parsed[i].get('faceId')
            faceRectangle=parsed[i].get('faceRectangle')
            faceAttributes=parsed[i].get('faceAttributes')
            rectangle.append(faceRectangle)
            Id.append(facesId)
            age.append(faceAttributes)
        return Id ,rectangle,age

    #检测相似度      
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
        #print(body)
        response=requests.request(self.Request_POST,API_URL,params=self.params,data=None,
                                  json=body,headers=headers)
        parsed=json.loads(response.text)
#        print(parsed)
        candidates=parsed[0].get('candidates')
        personId=candidates[0]['personId']
        confidence=candidates[0]['confidence']
        
        return personId,confidence
        
if __name__ == '__main__' :

    name_dict={"a83b8f8f-804f-4e67-aedc-f0c6ec9fe648":'handy',
                   "d69ddf9d-2415-43e2-8c8f-ee9d66cd3a1a":'yong',
                   "b0e7f2fa-445f-44c9-accc-f6adecc05144":'yan'}
    recongizer=FaceRecognizer('shinong_group')    
    image_path='2930.jpg'
    faceid,cc,age=recongizer.selectLocalFace(image_path)    
    image = cv2.imread(image_path)
    for ii,rectangle in enumerate(cc):
        x,y,w,h=rectangle['left'],rectangle['top'],rectangle['width'],rectangle['height']
        personId,confidence=recongizer.identifyFace2(faceid[ii])
        text=name_dict[personId]+'_age'+str(int(age[ii]['age']))              
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 3)       
        cv2.putText(image,text,(x,y),cv2.FONT_HERSHEY_PLAIN, 1.8, (0, 0, 255), 2)
    cv2.imwrite("19.jpg",image) #中文名字不能保存
    cv2.imshow("frame", image)    
    k=cv2.waitKey()  
    if k ==27:     # 键盘上Esc键的键值 
        cv2.destroyAllWindows()


