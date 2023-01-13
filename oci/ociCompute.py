import os, sys, time, logging, re
sys.path.append(os.environ['CLOUD_SRC'])
import oci, json, requests
from pushMessage.weChat import Message

logger = logging.getLogger(name='Default')
logger.setLevel(level=logging.DEBUG)
logger_Console_Handler = logging.StreamHandler()
logger_Console_Handler.setLevel(level=logging.DEBUG)
logger_Formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s %(message)s")
logger_Console_Handler.setFormatter(logger_Formatter)
logger.addHandler(logger_Console_Handler)

conf = os.path.join(os.path.split(sys.argv[0])[0], 'conf')
if not os.path.exists(conf):
    logger.warning('创建目录: %s' %conf)
    os.mkdir(conf)

cache = os.path.join(os.path.split(sys.argv[0])[0], 'cache')
if not os.path.exists(cache):
    logger.warning('创建目录: %s' %cache)
    os.mkdir(cache)

def notice(corpid, corpsecret, toWho, agentid, textContent):
    WeiXin = Message(corpid=corpid, corpsecret=corpsecret)
    access_token_file = os.path.join(cache, 'access.token')
    if not os.path.exists(access_token_file):
        fp = open(file=access_token_file, mode='w+', encoding='utf-8')
        fp.write(json.dumps(WeiXin.getAccessToken))
        fp.close()
        fp = open(file=access_token_file, mode='r+', encoding='utf-8')
        fp_content = fp.read()
        fp.close()
        logger.warning('写入访问令牌内容: %s' %fp_content)
    else:
        fp = open(file=access_token_file, mode='r+', encoding='utf-8')
        fp_content = fp.read()
        fp.close()
        if len(fp_content) != 284:
            logger.error('无效的访问令牌文件: %s' %access_token_file)
            logger.warning('重写访问令牌到文件: %s' %access_token_file)
            fp = open(file=access_token_file, mode='w+', encoding='utf-8')
            fp.write(json.dumps(WeiXin.getAccessToken))
            fp.close()
        else:
            logger.info('有效的访问令牌: %s' %fp_content)
    access_token_file_mtime = time.mktime(time.localtime(os.stat(access_token_file).st_mtime))
    access_token_file_check = time.mktime(time.localtime())
    access_token_file_diff_time = access_token_file_check - access_token_file_mtime
    if access_token_file_diff_time > 7200:
        logger.warning('访问令牌己过期: %s' %access_token_file_diff_time)
        fp = open(file=access_token_file, mode='w+', encoding='utf-8')
        fp.write(json.dumps(WeiXin.getAccessToken))
        fp.close()
        fp = open(file=access_token_file, mode='r+', encoding='utf-8')
        fp_content = fp.read()
        logger.warning('重写有效访问令牌: %s' %fp_content)
        fp.close()
    with open(file=access_token_file, mode='r+', encoding='utf-8') as fd:
        access_token = json.loads(fd.read())['access_token']
        logger.info(WeiXin.sendTextMessage(access_token=access_token, target=toWho, agentid=agentid, textContent=textContent))
        

def new_launch_instance():
    if os.path.exists(path='%s/.oci/config' %os.environ['HOME']):
        logger.info('读取来自oci配置文件: %s/.oci/config' %os.environ['HOME'])
        config = oci.config.from_file()
        logger.info('创建授权请求配置:')
        auth = oci.Signer(
            tenancy=config['tenancy'],
            user=config['user'],
            fingerprint=config['fingerprint'],
            private_key_file_location=config['key_file']
        )
        logger.info('授权租户: %s' %config['tenancy'])
        logger.info('授权用户: %s' %config['user'])
        logger.info('指纹信息: %s' %config['fingerprint'])
        logger.info('密钥位置: %s' %config['key_file'])
        endpoint = "https://iaas.ap-singapore-1.oraclecloud.com/20160918/instances/"
        inst_configure_file = os.path.join(conf, 'inst_configure.json')
        if os.path.exists(inst_configure_file):
            fp = open(file=inst_configure_file, mode='r+', encoding='utf-8')
            fp_content = fp.read()
            fp.close()
            #logger.info('New launch instance configure:\n%s' %fp_content)
            response = requests.post(url=endpoint, data=fp_content, auth=auth)
            #logger.info('Request return information: %s' %response.json())
            return response
        else:
            logger.error('读取新建实例配置文件失败')
            return None


def usage():
    print(f"Oracle Cloud 云平台工具使用方法：\n\
    {sys.argv[0]} [参数1] [子参数1] [子参数2]...\n\
    参数: --new-inst 在Oracle Cloud云平台新建实例\n \
         --new-inst子参数: [corpid: 企业微信的corpid], [corpsecret: 企业微信应用下的安全密钥], [toWho: 信息推送目标用户],\n\
         [agentid: 企业微信应用ID]"
         )

notice(corpid=sys.argv[2], corpsecret=sys.argv[3], toWho=sys.argv[4], agentid=sys.argv[5], textContent=logger.info('🏃‍♀️🏃‍♀️抢实例脚本开始启动啦'))

if len(sys.argv) < 2:
    usage()
elif len(sys.argv) == 6 and sys.argv[1] == '--new-inst':
    while True:
        rest = new_launch_instance().json()
        logger.info('实例创建请求结果: %s' %rest)
        if rest['code'] != 'InternalError' and rest['code'] != 'TooManyRequests':
            access_token_file = os.path.join(cache, 'access.token')
            fp = open(file=access_token_file, mode='r+', encoding='utf-8')
            fp_content = json.loads(fp.read())
            access_token = fp_content['access_token']
            fp.close()
            access_token_mtime = time.mktime(time.localtime(os.stat(path=access_token_file).st_mtime))
            current_time = time.mktime(time.localtime())
            diff_time = current_time - access_token_mtime
            message = f"📣Oracle Cloud 实例抢注通知\n\n请求结果: {rest}\n\n访问令牌: {access_token}\n\n令牌时差: {diff_time}"
            notice(corpid=sys.argv[2], corpsecret=sys.argv[3], toWho=sys.argv[4], agentid=sys.argv[5], textContent=message)
            break
        time.sleep(10)
else:
    usage()