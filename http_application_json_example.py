import requests
import json
import base64
from util.signature_util import generate_signature


# 读取文件内容，转为base64
def file_to_base64(filename):
    with open(filename, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


# http application/json webapi 示例代码
if __name__ == '__main__':
    url = "https://k8s.arity.cn/asr/http/asr/toText"
    # 业务方唯一标识id，最高128位，建议不要重复，这里只是模拟
    btId = "123"
    accessKey = "accessKey(请替换为正确的accessKey)"
    accessKeySecret = "accessKey(请替换为正确的accessKeySecret)"
    appCode = "appCode(请替换为正确的appCode)"
    channelCode = "channelCode(请替换为正确的channelCode)"

    headers = {"Content-Type": "application/json"}
    signResult = generate_signature(accessKey, accessKeySecret, appCode)
    data = {
        "btId": btId,
        "accessKey": accessKey,
        "appCode": appCode,
        "channelCode": channelCode,
        "contentType": "RAW",
        "formatInfo": "WAV",
        "content": file_to_base64("audio/ARITY2023S001W0001.wav"),
        "timestamp": signResult['timestamp'],
        "sign": signResult['signature']
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        if response_data["success"]:
            print("语音识别结果: {}".format(response_data["data"]["audioText"]))
        else:
            print("请求异常: {}".format(response_data))
    else:
        print("请求异常, httpCode: {}".format(response.status_code))
