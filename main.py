from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise

import auth
from app.models import *
from app.py_mod import *

authh = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()
register_tortoise(
    app,
    db_url="postgres://postgres:1234@localhost:5432/test_task",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.post("/first_user", tags=["First on"])
async def create_admin():
    try:
        user = await Users.create(
            super_user=True,
            user_name="admin",
            first_name="admin",
            last_name="admin",
            password=auth.get_pwd("admin"),
            is_active=True,
        )
        return "Admin created"
    except:
        raise HTTPException(status_code=422, detail="Admin user already exists")


@app.post("/login", tags=["Log In"])
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await Users.get(user_name=form_data.username)
        if auth.verif_pwd(form_data.password, user.password) and (user.super_user == True or user.is_active == True):
            token = auth.encoded_token(data={"sub": user.user_name, "activated": user.is_active})
            return {"access_token": token, "token_type": "Bearer"}
        # elif user.password=='admin' and (user.super_user == True or user.is_active==True) :
        #     token = auth.encoded_token(data={"sub": user.user_name, "activated": user.is_active})
        #     return {"access_token": token, "token_type": "Bearer"}
        else:
            raise HTTPException(status_code=404, detail="1Wrong login or password or user is not activated")
    except:
        raise HTTPException(status_code=404, detail="2Wrong login or password or user is not activated")


@app.get("/auth", tags=["Authorozation"])
async def authorize(token: str = Depends(authh)):
    return {"token": token}


@app.post("/create_user", tags=["CRUD"])
async def create_new_user(new_user: create_user, token: token = Depends(authh)):
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


@app.get("/all_users", tags=["CRUD"])
async def get_all_users(token: token = Depends(authh)):
    return await Users.all().values("id", "user_name", "first_name", "last_name", "is_active")


@app.get("/one_user/{user_id}", tags=["CRUD"])
async def get_one_user(user_id: int, token: token = Depends(authh)):
    try:
        get_user = await Users.get(id=user_id)
        return get_user
    except:
        raise HTTPException(status_code=404, detail="Incorrect id")


@app.put("/update_user/{user_id}", response_model=create_user, tags=["CRUD"])
async def update_user(user_id: int, user: create_user, token=Depends(authh)):
    try:
        get_user = await Users.get(id=user_id)
        await Users.filter(id=user_id).update(**user.dict())
        return await Users.get(id=user_id)
    except:
        new_user = await Users.create(
            id=user_id,
            user_name=user.user_name,
            first_name=user.first_name,
            last_name=user.last_name,
            password=auth.get_pwd(user.password),
        )
        return await new_user


@app.patch("/partly_update_user/{user_id}", response_model=update_user_pydantic, tags=["CRUD"])
async def partly_update_user(user_id: int, user: update_user_pydantic, token=Depends(authh)):
    try:
        for_update = {}
        user = user.dict()
        for k in user:
            if k == "password" and user[k] != None:
                for_update[k] = auth.get_pwd(user[k])
            elif user[k] != None:
                for_update[k] = user[k]

        await Users.get(id=user_id)
        await Users.filter(id=user_id).update(**for_update)
        return await Users.get(id=user_id)
    except:
        raise HTTPException(status_code=404, detail="No such id")


@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, token: token = Depends(authh)):
    deleted_count = await Users.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return f"Deleted user {user_id}"
