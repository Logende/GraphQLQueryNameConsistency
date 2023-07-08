class Operation:
    def __init__(self, operation_type, operation_name, content, metadata):
        self.operation_type = operation_type
        self.operation_name = operation_name
        self.content = content
        self.metadata = metadata

    def to_dict(self):
        return {
            "type": self.operation_type,
            "name": self.operation_name,
            "content": self.content,
            "metadata": self.metadata
        }


class Fragment:
    def __init__(self, content, metadata):
        self.content = content
        self.metadata = metadata

    def to_dict(self):
        return {
            "content": self.content,
            "metadata": self.metadata
        }
