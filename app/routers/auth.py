from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt

from app.database.deps import get_uow
from app.auth.session import create_session_token
from app.auth.deps import COOKIE_NAME

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    uow=Depends(get_uow),
):
    with uow.start():
        user = uow.users.get_by_username(username)
        if not user or not bcrypt.verify(password, user.hashed_password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid username or password"},
                status_code=401,
            )
        if not user.is_active:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Account is deactivated"},
                status_code=401,
            )

        token = create_session_token(user.id)
        response = RedirectResponse("/", status_code=302)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            # secure=True,  # Enable in production with HTTPS
        )
        return response


@router.get("/logout")
@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(key=COOKIE_NAME)
    return response
