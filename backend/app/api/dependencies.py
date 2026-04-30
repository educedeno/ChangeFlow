def get_change_request_repository():
    class FakeRepository:
        def __init__(self):
            self.data = []

        def save(self, change_request):
            self.data.append(change_request)

        def get_all(self):
            return self.data

        def get_by_id(self, request_id):
            for cr in self.data:
                if cr.id == request_id:
                    return cr
            return None

    return FakeRepository()