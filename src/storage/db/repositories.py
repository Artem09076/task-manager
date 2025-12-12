from sqlalchemy.ext.asyncio import AsyncSession 
from src.storage.db.model.models import User, Project, Task, Intergration, Event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, project_id: str, title: str, description: str, source: str, external_id) -> Task:
        task = Task(project_id=project_id, title=title, description=description, source=source, external_id=external_id)
        try:
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)
            return task
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise 
        except Exception as e:
            await self.db.rollback()
            raise
    
    async def create_or_update_from_external(self, source: str, external_id: str, repo_full_name: str, title: str, description: str) -> Task:
        intergration = await self.db.scalar(
            select(Intergration)
            .where(Intergration.type == source)
            .where(Intergration.external_id == repo_full_name)
            .where(Intergration.enabled == True)
        )
        if not intergration:
            raise ValueError("No enabled integration found for the given source and repository.")
        
        project_id = intergration.project_id
        
        q = (
            select(Task)
            .where(Task.source == source)
            .where(Task.external_id == external_id)
        )

        result = await self.db.execute(q)
        task = result.scalar_one_or_none()
        if not task:
            task = await self.create_task(title=title, description=description, source=source, external_id=external_id, project_id=project_id)
        else:
            task.title = title
            task.description = description
        
        await self.db.commit()
        return task
    async def update_status_from_external(self, repo_full_name: str, external_id: str, status) -> Task:
        intergration = await self.db.scalar(
            select(Intergration)
            .where(Intergration.type == "github")
            .where(Intergration.external_id == repo_full_name)
            .where(Intergration.enabled == True)
        )
        if not intergration:
            raise ValueError("No enabled integration found for the given source and repository.")
        
        q = (
            select(Task)
            .where(Task.source == "github")
            .where(Task.external_id == external_id)
        )

        result = await self.db.execute(q)
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError("Task not found for the given external ID.")
        
        task.status = status
        await self.db.commit()
        return task
    
    async def delete_task_from_external(self, repo_full_name: str, external_id: str) -> None:
        intergration = await self.db.scalar(
            select(Intergration)
            .where(Intergration.type == "github")
            .where(Intergration.external_id == repo_full_name)
            .where(Intergration.enabled == True)
        )
        if not intergration:
            raise ValueError("No enabled integration found for the given source and repository.")
        
        q = (
            select(Task)
            .where(Task.source == "github")
            .where(Task.external_id == external_id)
        )

        result = await self.db.execute(q)
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError("Task not found for the given external ID.")
        
        await self.db.delete(task)
        await self.db.commit()
    

class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_task_by_id(self, task_id: str) -> Task | None:
        try:
            res = await self.db.execute(select(Task).where(Task.id == task_id))
            task = res.scalars().first()
            return task
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise
    
    async def get_user_by_username(self, username: str) -> User | None:
        try:
            res = await self.db.execute(select(User).where(User.username == username))
            user = res.scalars().first()
            return user
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise

class IntegrationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    
   
    