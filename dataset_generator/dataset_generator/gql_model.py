class Operation:
    def __init__(self, operation_type, operation_name, content):
        self.operation_type = operation_type
        self.operation_name = operation_name
        self.content = content

    def to_dict(self):
        return {
            "type": self.operation_type,
            "name": self.operation_name,
            "content": self.content
        }


class Fragment:
    def __init__(self, content):
        self.content = content

    def to_dict(self):
        return {
            "content": self.content
        }
