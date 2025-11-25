def success(data=None, message="success"):
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error(data=None, message="error"):
    return {
        "success": False,
        "message": message,
    }