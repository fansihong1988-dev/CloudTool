import os, sys, time
sys.path.append(os.environ['CLOUD_SRC'])
import oci, json, requests
from pushMessage.weChat import Message

conf = os.path.join(os.path.split(sys.argv[0])[0], 'conf')
if not os.path.exists(conf):
    os.mkdir(conf)
cache = os.path.join(os.path.split(sys.argv[0])[0], 'cache')
if not os.path.exists(cache):
    os.mkdir(cache)

def launchInstance(corpid, corpsecret):
    config = oci.config.from_file()
    auth = oci.Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file']
    )
    endpoint = "https://iaas.ap-singapore-1.oraclecloud.com/20160918/instances/"
    launchInstanceConf = os.path.join(conf, 'launchInstance.json')
    fd1 = open(file=launchInstanceConf, mode='r+', encoding='utf-8')
    fd1Content = fd1.read()
    fd1.close()
    response = requests.post(url=endpoint, data=fd1Content, auth=auth)
    WeiXin = Message(corpid=corpid, corpsecret=corpsecret)
    access_token_file = os.path.join(cache, 'access.token')
    while True:
        if response.status_code == 200:
            if not os.path.exists(access_token_file):
                accessTokenFP = open(file=access_token_file, mode='w+', encoding='utf-8')
                accessTokenFP.write(json.dumps(WeiXin.getAccessToken))
                accessTokenFP.close()
            access_token_previous_time = time.mktime(time.localtime(os.stat(access_token_file).st_mtime))
            current_local_time = time.mktime(time.localtime())
            difference_time = current_local_time - access_token_previous_time
            if difference_time >= 7200:
                accessTokenRewriteFP = open(file=access_token_file, mode='w+', encoding='utf-8')
                accessTokenRewriteFP.write(json.dumps(WeiXin.getAccessToken))
                accessTokenRewriteFP.close()
            accessTokenRead = open(file=access_token_file, mode='r+', encoding='utf-8')
            validAccesssToken = json.loads(accessTokenRead.read())['access_token']
            accessTokenRead.close()
            WeiXin.sendTextMessage(
                access_token=validAccesssToken,
                target='FanSiHong',
                agentid=1000003,
                textContent=f"🎉🎉🎉🎉OCI实例注册成功\n\n🖥️实例信息: {response.text}\n🔑令牌信息: {validAccesssToken}\n⏰令牌间隔: {difference_time}"
            )
            break
        time.sleep(10)

if sys.argv[1] == "--new-instance":
    launchInstance(corpid=sys.argv[2], corpsecret=sys.argv[3])
else:
    print(
        "--new-instance: 创建新实例, 需要传入corpid, 和corpsecret"
    )