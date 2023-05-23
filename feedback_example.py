import requests
import json
from util.signature_util import generate_signature

# 语音识别反馈 webapi 示例代码
if __name__ == '__main__':
    url = "https://k8s.arity.cn/asr/http/asr/V1/feedback"
    # 对应语音识别时传的的btId
    btId = "btId(请替换为正确的btId)"
    # 对应语音识别返回的requestId
    requestId = "requestId(请替换为正确的requestId)"
    # 是否识别准确 0: 准确 1: 不准确
    exactType = 1
    accessKey = "accessKey(请替换为正确的accessKey)"
    accessKeySecret = "accessKey(请替换为正确的accessKeySecret)"
    appCode = "appCode(请替换为正确的appCode)"
    channelCode = "channelCode(请替换为正确的channelCode)"

    headers = {"Content-Type": "application/json"}
    signResult = generate_signature(accessKey, accessKeySecret, appCode)
    data = {
        "btId": btId,
        "requestId": requestId,
        "accessKey": accessKey,
        "appCode": appCode,
        "channelCode": channelCode,
        "timestamp": signResult['timestamp'],
        "sign": signResult['signature'],
        "exactType": exactType
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        if response_data["success"]:
            print("反馈成功")
        else:
            print("反馈异常: {}".format(response_data))
    else:
        print("请求异常, httpCode: {}".format(response.status_code))
