from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise

import auth
from app.models import *

authh = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()
register_tortoise(
    app,
    db_url="postgres://postgres:1234@localhost:5432/test_task",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.post("/create_user", tags=["createUser"])
async def create_user(new_user: create_user):
    try:
        user = await Users.create(
            user_name=new_user.user_name,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            password=auth.get_pwd(new_user.password),
        )
        return user
    except:
        raise HTTPException(status_code=404, detail="Incorrect data")


@app.post("/login", tags=["Log In"])
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await Users.get(user_name=form_data.username)
        if auth.verif_pwd(form_data.password, user.password) and user.is_active == True:
            token = auth.encoded_token(data={"sub": user.user_name, "activated": user.is_active})
            return {"access_token": token, "token_type": "Bearer"}
        else:
            raise HTTPException(status_code=404, detail="Wrong login or password or user is not activated")
    except:
        raise HTTPException(status_code=404, detail="Wrong login or password or user is not activated")


@app.get("/auth", tags=["Authorozation"])
async def authorize(token: str = Depends(authh)):
    return {"token": token}


async def check_acsess(user: token = Depends(authorize)):
    tok = auth.decoded_token(user["token"])
    us_name = tok["sub"]
    user_inf = await Users.get(user_name=us_name)
    print(f"activated: {user_inf.is_active}")
    return user_inf.is_active


@app.get("/all_users", tags=["CRUD"])
async def get_all_users(user: token = Depends(check_acsess)):
    if user == True:
        return await Users.all().values("id", "user_name", "first_name", "last_name", "is_active")
