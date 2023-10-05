class ResponseModel:
    code = 1
    data = ''
    message = ''

    def __init__(self, code, data, message):  # 必须要有一个self参数，
        self.code = code
        self.data = data
        self.message = message

    def toJson(self):
        return {'code': self.code, 'data': self.data, 'message': self.message}
