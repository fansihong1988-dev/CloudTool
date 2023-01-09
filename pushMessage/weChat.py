import requests

class Message:
    
    def __init__(self, corpid, corpsecret) -> None:
        self.corpid = corpid
        self.corpsecret = corpsecret
    
    @property
    def getAccessToken(self):
        endpoint = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?"
        params = {
            "corpid": self.corpid,
            "corpsecret": self.corpsecret
        }
        response = requests.get(url=endpoint, params=params).json()
        return response
        
    def sendTextMessage(self, access_token, target, agentid, textContent):
        endpoint = "https://qyapi.weixin.qq.com/cgi-bin/message/send?"
        params = {
            "access_token": access_token
        }
        data = {
            "touser": target,
            "agentid": agentid,
            "msgtype": "text",
            "text": {
                "content": textContent
            },
            "safe": 0
        }
        response = requests.post(url=endpoint, params=params, json=data).json()
        return response