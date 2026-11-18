from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response( message: str = "success",data = None):
    content = {
        "code": 200,
        "data": data,
        "message": message
    }
    return JSONResponse(content=jsonable_encoder(content))