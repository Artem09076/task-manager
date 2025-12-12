from sqlalchemy.ext.asyncio import AsyncSession 
from src.storage.db.model.models import User, Project, Task, Intergration, Event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

class Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        try: 
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise 
        except Exception as e:
            await self.db.rollback()
            raise

    async def get_user_by_id(self, user_id: str) -> User | None:
        try:
            res = await self.db.execute(select(User).where(User.id == user_id))
            user = res.scalars().first()
            return user
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise
    
    async def create_project(self, name: str, owner_id: str) -> Project:
        project = Project(name=name, owner_id=owner_id)
        try:
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)
            return project
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise 
        except Exception as e:
            await self.db.rollback()
            raise
    
    async def get_project_by_id(self, project_id: str) -> Project | None:
        try:
            res = await self.db.execute(select(Project).where(Project.id == project_id))
            project = res.scalars().first()
            return project
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise
    
    async def create_task(self, project_id: str, title: str, description: str, created_by: str) -> Task:
        task = Task(project_id=project_id, title=title, description=description, created_by=created_by)
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
    
    async def get_task_by_id(self, task_id: str) -> Task | None:
        try:
            res = await self.db.execute(select(Task).where(Task.id == task_id))
            task = res.scalars().first()
            return task
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise
    
    async def create_integration(self, project_id: str, type: str, external_id: str, config: dict) -> Intergration:
        integration = Intergration(project_id=project_id, type=type, external_id=external_id, config=config)
        try:
            self.db.add(integration)
            await self.db.commit()
            await self.db.refresh(integration)
            return integration
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise 
        except Exception as e:
            await self.db.rollback()
            raise
    
    async def get_integration_by_id(self, integration_id: str) -> Intergration | None:
        try:
            res = await self.db.execute(select(Intergration).where(Intergration.id == integration_id))
            integration = res.scalars().first()
            return integration
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise  
    
    async def create_event(self, task_id: str) -> Event:
        event = Event(task_id=task_id)
        try:
            self.db.add(event)
            await self.db.commit()
            await self.db.refresh(event)
            return event
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise 
        except Exception as e:
            await self.db.rollback()
            raise
    
    async def get_event_by_id(self, event_id: str) -> Event | None:
        try:
            res = await self.db.execute(select(Event).where(Event.id == event_id))
            event = res.scalars().first()
            return event
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
