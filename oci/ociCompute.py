import os, sys, time, logging
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
    logger.warning('%s will be created' %conf)
    os.mkdir(conf)

cache = os.path.join(os.path.split(sys.argv[0])[0], 'cache')
if not os.path.exists(cache):
    logger.warning('%s Will be created' %cache)
    os.mkdir(cache)

def notice(corpid, corpsecret):
    WeiXin = Message(corpid=corpid, corpsecret=corpsecret)
    access_token_file = os.path.join(cache, 'access.token')
    if os.path.exists(access_token_file):
        fp = open(file=access_token_file, mode='r+', encoding='utf-8')
        fp_content = fp.read()
        fp.close()
        logger.info('Access token read: %s' %fp_content)
    else:
        fp = open(file=access_token_file, mode='w+', encoding='utf-8')
        fp_content = fp.write(json.dumps(WeiXin.getAccessToken))
        fp.close()
        logger.info('Access token write: %s' %fp_content)
    
   

def new_launch_instance():
    if os.path.exists(path='%s/.oci/config' %os.environ['HOME']):
        logger.info('Read oci configure from %s/.oci/config' %os.environ['HOME'])
        config = oci.config.from_file()
        logger.info('Create request authorized configure from config')
        auth = oci.Signer(
            tenancy=config['tenancy'],
            user=config['user'],
            fingerprint=config['fingerprint'],
            private_key_file_location=config['key_file']
        )
        logger.info('authorized tenancy: %s' %config['tenancy'])
        logger.info('authorized user: %s' %config['user'])
        logger.info('authorized fingerprint: %s' %config['fingerprint'])
        logger.info('authorized private_key_file_location: %s' %config['key_file'])
        endpoint = "https://iaas.ap-singapore-1.oraclecloud.com/20160918/instances/"
        inst_configure_file = os.path.join(conf, 'inst_configure.json')
        if os.path.exists(inst_configure_file):
            fp = open(file=inst_configure_file, mode='r+', encoding='utf-8')
            fp_content = fp.read()
            fp.close()
            #logger.info('New launch instance configure:\n%s' %fp_content)
            response = requests.post(url=endpoint, data=fp_content, auth=auth)
            logger.info('Request return information: %s' %response.json())
            return response
        else:
            logger.error('Read launch new instance configure failed')