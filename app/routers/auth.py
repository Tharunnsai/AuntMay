from fastapi import APIRouter

from ..schemas import SignupRequest, SignupResponse, LoginRequest, LoginResponse
from ..store import HARDCODED_USER_ID, HARDCODED_ACCESS_TOKEN


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(payload: SignupRequest):
    return SignupResponse(message="User created successfully.", userId=HARDCODED_USER_ID)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    return LoginResponse(message="Login successful.", accessToken=HARDCODED_ACCESS_TOKEN)


