class ApiResult:
    def __init__(self, success, status='', data=None):
        self.success = success
        self.status = status
        self.data = data

    def __repr__(self):
        return {'success': self.success, 'status': self.status, 'data': self.data}
