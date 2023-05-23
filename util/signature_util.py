import hashlib
import time


# 生成签名
def generate_signature(accessKey, accessKeySecret, appCode):
    timestamp = int(round(time.time() * 1000))

    # 将签名参数按照字典序排序
    params = {
        'accessKey': accessKey,
        'accessKeySecret': accessKeySecret,
        'appCode': appCode,
        'timestamp': timestamp
    }
    sorted_params = dict(sorted(params.items()))

    # 拼接排序后的参数
    sign_str = ''
    for key, value in sorted_params.items():
        sign_str += key + str(value)

    # 计算签名
    md5_str = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    return {
        'signature': md5_str,
        'timestamp': timestamp
    }
