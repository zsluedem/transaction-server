import uvicorn
from rserver.app import app
from rserver.config import setting

if __name__ == '__main__':
    uvicorn.run(app, host=setting.HOST, port=setting.PORT)