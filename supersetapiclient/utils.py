import shortuuid
def generate_uuid(_type):
    return f"{_type}-{shortuuid.ShortUUID().random(length=10)}"