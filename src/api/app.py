from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ..data.user_manager import UserManager
from ..core.ai_agent import JobSearchAgent
from ..core.job_search_engine import JobSearchEngine
from ..core.application_manager import ApplicationManager
from .schemas import (
    UserProfile,
    SearchRequest,
    ApplyRequest,
    ApplicationRecord,
)


app = FastAPI(
    title="Auto Job Apply - API",
    description="FastAPI backend for the Auto Job Apply and Recommendation System",
    version="0.1.0",
)

# Allow all origins for development; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate core components
user_manager = UserManager()
ai_agent = JobSearchAgent()
job_engine = JobSearchEngine()
application_manager = ApplicationManager()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users", response_model=List[UserProfile])
def list_users():
    users = user_manager.get_all_users()
    return users


@app.get("/users/{user_id}", response_model=UserProfile)
def get_user(user_id: str):
    user = user_manager.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserProfile)
def create_user(user: UserProfile):
    data = user.model_dump()
    success = user_manager.add_user(data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add user")
    # Return the newly added user (last one)
    return user_manager.get_all_users()[-1]


@app.post("/search")
def search_jobs(req: SearchRequest):
    # Resolve user profile
    user_profile = None
    if req.user_id:
        user_profile = user_manager.get_user_by_id(req.user_id)
    elif req.user_profile:
        user_profile = req.user_profile.model_dump()
    else:
        raise HTTPException(status_code=400, detail="Provide user_id or user_profile")

    # Create search strategy
    strategy = ai_agent.create_search_strategy(user_profile)

    # Determine query
    query = req.query or (user_profile.get('preferred_roles') or [None])[0]

    jobs = job_engine.search_jobs(query=query, location=req.location, skills=user_profile.get('skills')) # type: ignore

    return {"strategy": strategy, "jobs": jobs}


@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: str, limit: int = 5):
    user = user_manager.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = (user.get('preferred_roles') or [None])[0]
    jobs = job_engine.search_jobs(query=query, skills=user.get('skills')) # type: ignore
    ranked = ai_agent.rank_jobs(user, jobs)

    return {"recommendations": ranked[:limit]}


@app.post("/apply")
def apply(req: ApplyRequest):
    # Resolve user profile
    user_profile = None
    if req.user_id:
        user_profile = user_manager.get_user_by_id(req.user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
    elif req.user_profile:
        user_profile = req.user_profile.model_dump()
    else:
        raise HTTPException(status_code=400, detail="Provide user_id or user_profile")

    success = application_manager.apply_to_job(req.job.model_dump(), user_profile)
    if not success:
        raise HTTPException(status_code=500, detail="Application failed")


@app.get("/applications", response_model=List[ApplicationRecord])
def list_applications():
    return application_manager.get_application_history()
