import requests
from util.signature_util import generate_signature

# http form-data webapi 示例代码
if __name__ == '__main__':
    url = "https://k8s.arity.cn/asr/http/asr/toTextBinary"
    # 业务方唯一标识id，最高128位，建议不要重复，这里只是模拟
    btId = "123"
    accessKey = "accessKey(请替换为正确的accessKey)"
    accessKeySecret = "accessKey(请替换为正确的accessKeySecret)"
    appCode = "appCode(请替换为正确的appCode)"
    channelCode = "channelCode(请替换为正确的channelCode)"

    headers = {}
    signResult = generate_signature(accessKey, accessKeySecret, appCode)
    data = {
        "btId": (None, btId),
        "accessKey": (None, accessKey),
        "appCode": (None, appCode),
        "channelCode": (None, channelCode),
        "timestamp": (None, signResult['timestamp']),
        "sign": (None, signResult['signature']),
        "sampleRateEnum": "SAMPLE_RATE_16K"
    }
    files = {
        "file": ("BAC009S0002W0164.wav", open("audio/BAC009S0002W0164.wav", "rb"), 'application/octet-stream')
    }
    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        response_data = response.json()
        if response_data["success"]:
            print("语音识别结果: {}".format(response_data["data"]["audioText"]))
        else:
            print("请求异常: {}".format(response_data))
    else:
        print("请求异常, httpCode: {}".format(response.status_code))
