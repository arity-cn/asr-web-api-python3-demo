import argparse
import json
from urllib.parse import urlencode
import websocket
from websocket import ABNF

from util.signature_util import generate_signature

# 识别结果
result = []


# 构建请求参数，获取携带参数的ws url
def get_websocket_url(websocket_url, bt_id, access_key, access_key_secret, app_code, channel_code):
    # 签名
    sign_result = generate_signature(access_key, access_key_secret, app_code)
    params = {
        "accessKey": access_key, "appCode": app_code, "channelCode": channel_code,
        "btId": bt_id, "sign": sign_result['signature'], "timestamp": sign_result['timestamp']
    }
    return f"{websocket_url}?{urlencode(params)}"


# 构建开始报文
def build_start_frame():
    business = {
        'vadEos': 5000
    }
    data = {
        'audioFormatInfo': 'WAV',
        'sampleRate': 'SAMPLE_RATE_16K'
    }
    frame = {
        'signal': 'start',
        'business': business,
        'data': data
    }
    return json.dumps(frame)


# 构建结束报文
def build_end_frame():
    frame = {
        'signal': 'end'
    }
    return json.dumps(frame)


# 处理验证结果报文
def after_process_verify(ws, message_obj):
    # 处理验证结果逻辑：验证成功发送开始报文，验证失败打印错误信息
    if message_obj.status == 'ok':
        print(f"校验通过，requestId: {message_obj.requestId}, code: {message_obj.code}")
        ws.send(build_start_frame())
    else:
        print(f"校验失败，requestId: {message_obj.requestId}, code: {message_obj.code}, message: {message_obj.message}")


# 处理准备好进行语音识别报文
def after_process_server_ready(ws, message_obj):
    # 处理服务端准备好进行语音识别报文，发送二进制报文，发送完二进制报文后发送结束识别报文
    print("处理服务端准备好进行语音识别报文")
    if message_obj.status == 'ok':
        with open("audio/ARITY2023S001W0001.wav", "rb") as f:
            # 每次读取10k字节
            while True:
                chunk = f.read(10240)
                if not chunk:
                    # 读取结束，跳出循环
                    break
                # 发送二进制报文
                ws.send(chunk, opcode=ABNF.OPCODE_BINARY)
        # 发送结束识别报文
        ws.send(build_end_frame())
    else:
        print(f"服务器准备失败, 报文: {message_obj}")


# 处理中间识别结果报文
def after_process_partial_result(ws, message_obj):
    print("处理中间结果报文")
    nbest = json.loads(message_obj.nbest)
    sentence = nbest[0]['sentence']
    if len(sentence) == 0:
        print("没有识别出结果，跳过此次中间结果报文处理")
        return
    if len(result) > 0:
        print(f"当前语音识别结果：{''.join(result)}，{sentence}")
    else:
        print(f"当前语音识别结果：{sentence}")


# 处理最终识别结果报文
def after_process_final_result(ws, message_obj):
    print("处理最终结果报文")
    nbest = json.loads(message_obj.nbest)
    sentence = nbest[0]['sentence']
    if len(sentence) == 0:
        print("没有识别出结果，跳过此次最终结果报文处理")
        return
    if len(result) > 0:
        result.append('，')
        result.append(sentence)
        print(f"当前语音识别结果：{''.join(result)}")
    else:
        result.append(sentence)
        print(f"当前语音识别结果：{''.join(result)}")


# 处理识别结束报文
def after_process_speech_end(ws, message_obj):
    print("收到识别结束报文")
    if len(result) > 0:
        result.append('。')
    print(f"最终语音识别结果：{''.join(result)}")
    ws.close()


def on_message(ws, message):
    # 在这里处理WebSocket消息
    print("接收到消息：{}".format(message))
    message_obj = json.loads(message)
    message_obj = argparse.Namespace(**message_obj)
    # 消息分发
    if message_obj.type == 'verify':
        after_process_verify(ws, message_obj)
    elif message_obj.type == 'server_ready':
        after_process_server_ready(ws, message_obj)
    elif message_obj.type == 'partial_result':
        after_process_partial_result(ws, message_obj)
    elif message_obj.type == 'final_result':
        after_process_final_result(ws, message_obj)
    elif message_obj.type == 'speech_end':
        after_process_speech_end(ws, message_obj)


def on_close(ws):
    print('websocket连接关闭')


def on_error(ws, error):
    print(f"websocket发生异常: {error}")


# websocket webapi 示例代码
if __name__ == '__main__':
    url = "wss://k8s.arity.cn/asr/ws"
    # 业务方唯一标识id，最高128位，建议不要重复，这里只是模拟
    btId = "123"
    accessKey = "accessKey(请替换为正确的accessKey)"
    accessKeySecret = "accessKey(请替换为正确的accessKeySecret)"
    appCode = "appCode(请替换为正确的appCode)"
    channelCode = "channelCode(请替换为正确的channelCode)"

    complete_url = get_websocket_url(url, btId, accessKey, accessKeySecret, appCode, channelCode)
    print(f"构建参数后的url: {complete_url}")
    # 创建WebSocket实例
    ws = websocket.WebSocketApp(complete_url, on_message=on_message, on_close=on_close, on_error=on_error)
    # 连接WebSocket服务端
    ws.run_forever()
