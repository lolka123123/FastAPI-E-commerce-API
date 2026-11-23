from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.service import AuthService, RegisterStatus
from app.auth.schemas import RegisterRequest, TokenPair, RefreshRequest, VerifyEmailRequest, ResendVerificationRequest, \
    ChangePasswordRequest, ChangeEmailRequest, ConfirmEmailChangeRequest
from app.users.schemas import UserResponse
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service: Annotated[AuthService, Depends(get_auth_service)]):
    result = await service.register(data)
    if result is RegisterStatus.ALREADY_REGISTERED:
        raise HTTPException(
            status_code=409,
            detail='Email already registered'
        )
    if result is RegisterStatus.RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail='Please wait before requesting another verification email'
        )
    return  {"message": "Verification email sent"}



@router.post('/login', response_model=TokenPair)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                service: Annotated[AuthService, Depends(get_auth_service)]):
    tokens = await service.login(
        email=form_data.username,
        password=form_data.password
    )

    if tokens is None:
        raise HTTPException(
            status_code=401,
            detail='Incorrect email or password',
            headers={"WWW-Authenticate": "Bearer"}
        )

    return tokens

@router.post('/refresh', response_model=TokenPair)
async def refresh(data: RefreshRequest,
                  service: Annotated[AuthService, Depends(get_auth_service)]):
    tokens = await service.refresh(data.refresh_token)

    if tokens is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid or expired refresh token'
        )

    return tokens

@router.post('/verify-email')
async def verify_email(
        data: VerifyEmailRequest,
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    is_verified = await service.verify_email(data.token)

    if not is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired verification token'
        )
    return {'message': 'Email successfully verified'}


@router.post('/resend-verification')
async def resend_verification(
        data: ResendVerificationRequest,
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    result = await service.resend_verification(data.email)

    if result is RegisterStatus.RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail='Please wait before requesting another verification email'
        )

    return {'message': (
        'If the account exists and is not verified, '
        'a verification email has been sent.'
    )}

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        data: RefreshRequest,
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    await service.logout(data.refresh_token)

@router.post('/logout-all', status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
        current_user: Annotated[User, Depends(get_current_user)],
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    await service.logout_all(current_user.id)

@router.patch('/change-password')
async def change_password(
        data: ChangePasswordRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    success = await service.change_password(
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail='Unable to change password'
        )

    return {'message': 'Password successfully changed'}


@router.post('/change-email')
async def request_email_change(
        data: ChangeEmailRequest,
        current_user: Annotated[User, Depends(get_current_user)],
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    success = await service.request_email_change(
        user=current_user,
        new_email=str(data.new_email),
        current_password=data.current_password
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail='Unable to change email',
        )

    return {'message': 'Confirmation email sent to your new email address'}




@router.post('/confirm-email-change')
async def confirm_email_change(
        data: ConfirmEmailChangeRequest,
        service: Annotated[AuthService, Depends(get_auth_service)]
):
    success = await service.confirm_email_change(data.token)

    if not success:
        raise HTTPException(
            status_code=400,
            detail='Invalid or expired token',
        )

    return {'message': 'Email successfully changed'}


# @router.post('/delete-user')
# async def delete_user(
#         data: ResendVerificationRequest,
#         service: Annotated[AuthService, Depends(get_auth_service)]
# ):
#     success =  await service.delete_user(data.email)
#     if not success:
#         return {'message': 'NO'}
#
#     return {'message': 'ok'}