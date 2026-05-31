from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from shared.auth.jwt import (
    create_access_token,
    get_current_user,
    UserInToken,
)

from apps.db.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserProfileResponse,
    ProfileUpdateRequest,
)

from apps.db.services.auth_service import (
    AuthService,
)

from apps.db.dependencies import (
    get_auth_service,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    auth_service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Register a new farmer account.
    """

    try:

        user = await auth_service.register(
            name=body.name,
            email=body.email,
            password=body.password,
            phone=body.phone,
            location=body.location,
            primary_crops=body.primary_crops,
            land_size_acres=body.land_size_acres,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    token = create_access_token(
        {
            "sub": user.farmer_id,
            "name": user.name,
            "role": user.role,
        }
    )

    return TokenResponse(
        access_token=token,
        farmer_id=user.farmer_id,
        name=user.name,
        role=user.role,
    )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Login using email/password.
    """

    try:

        user = await auth_service.login(
            email=body.email,
            password=body.password,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    token = create_access_token(
        {
            "sub": user.farmer_id,
            "name": user.name,
            "role": user.role,
        }
    )

    return TokenResponse(
        access_token=token,
        farmer_id=user.farmer_id,
        name=user.name,
        role=user.role,
    )


# ============================================================
# CURRENT PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=UserProfileResponse,
)
async def get_profile(
    current_user: UserInToken = Depends(
        get_current_user
    ),
    auth_service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Retrieve current user profile.
    """

    user = await auth_service.get_profile(
        current_user.farmer_id
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserProfileResponse.model_validate(
        user
    )


# ============================================================
# UPDATE PROFILE
# ============================================================

@router.put(
    "/me",
    response_model=UserProfileResponse,
)
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    auth_service: AuthService = Depends(
        get_auth_service
    ),
):
    """
    Update farmer profile.
    """

    updates = body.model_dump(
        exclude_none=True
    )

    user = await auth_service.update_profile(
        farmer_id=current_user.farmer_id,
        updates=updates,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserProfileResponse.model_validate(
        user
    )


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
async def logout(
    current_user: UserInToken = Depends(
        get_current_user
    ),
):
    """
    Stateless JWT logout.

    Future enhancement:
    Store JWT in Redis blacklist.
    """

    return {
        "message": (
            f"Successfully logged out, "
            f"{current_user.name}"
        )
    }


# ============================================================
# DEMO USERS
# ============================================================

@router.get("/demo-credentials")
async def demo_credentials():

    return {
        "message": (
            "Use these credentials "
            "for testing."
        ),
        "demo_farmer": {
            "email": "demo@krishimind.ai",
            "password": "demo1234",
        },
        "demo_admin": {
            "email": "admin@krishimind.ai",
            "password": "admin1234",
        },
    }