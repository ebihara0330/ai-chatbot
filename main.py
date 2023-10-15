from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
app = FastAPI()

security = HTTPBasic()
templates = Jinja2Templates(directory="templates")  # UIファイルのディレクトリを指定

# def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
#     correct_username = "username"
#     correct_password = "password"
#     if credentials.username != correct_username or credentials.password != correct_password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Basic"},
#         )
#     return credentials.username

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("chatbot_ui.html", {"request": request})