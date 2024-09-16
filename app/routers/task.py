from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.backend.db_depends import get_db
from app.models import Task, User
from app.schemas import CreateTask

router = APIRouter(
    prefix="/task",
    tags=["task"]
)


@router.get('/')
async def all_tasks(db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/{task_id}')
async def task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post('/create')
async def create_task(task: CreateTask, user_id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    new_task = Task(**task.dict(), user_id=user_id)
    db.add(new_task)
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update/{task_id}')
async def update_task(task_id: int, task: CreateTask, db: Session = Depends(get_db)):
    task_to_update = db.scalar(select(Task).where(Task.id == task_id))

    if task_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    for key, value in task.dict().items():
        setattr(task_to_update, key, value)

    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task update is successful'}


@router.delete('/delete/{task_id}')
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_to_delete = db.scalar(select(Task).where(Task.id == task_id))
    if task_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task_to_delete)
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task delete is successful'}
