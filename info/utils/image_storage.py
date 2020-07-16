from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'N07uQaQLNkEvmCVriJjCcuXhGN7bfo04A8lYlog6'
secret_key = 'N7VvEn2iRZEh9KWSQxsk6rxdDpZFUM-tCxCWrSsB'
# 要上传的空间
bucket_name = '2500082520'


def storage(data):
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, None, 3600)
        # 要上传文件的本地路径
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    # localfile = '/home/python/Desktop/touxiang.jpg'
    localfile = input("请输入文件路径:")
    with open(localfile, 'rb') as f:
        storage(f.read())


