from ronglian_sms_sdk import SmsSDK

accId = '8a216da8759c87cc0175d178d92f1013'
accToken = 'ce76892cb82648b2886ac12dc327997f'
appId = '8a216da8759c87cc0175d178da15101a'


def send_message(mobile, sms_code):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    mobiles = f'{mobile}'
    datas = (f'{sms_code}', '1')
    resp = sdk.sendMessage(tid, mobiles, datas)
    print(resp)
