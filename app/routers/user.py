from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.backend.db_depends import get_db
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if result:
        return result
    raise HTTPException(status_code=404, detail="User was not found")


@router.post("/create")
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update/{user_id}")
async def update_user(user_id: int, user_updates: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User was not found")

    for key, value in user_updates.dict().items():
        setattr(existing_user, key, value)

    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}


@router.delete('/delete/{user_id}')
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_to_delete = db.scalar(select(User).where(User.id == user_id))
    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.execute(delete(Task).where(Task.user_id == user_id))

    db.delete(user_to_delete)
    db.commit()

    return {'status_code': status.HTTP_200_OK, 'transaction': 'User and associated tasks delete is successful'}



@router.get('/{user_id}/tasks')
async def tasks_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks
