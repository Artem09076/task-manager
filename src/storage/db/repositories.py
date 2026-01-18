from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.integration import IntegrationCreate, IntegrationUpdate
from src.storage.db.model.models import Event, Integration
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from src.storage.db.model.models import TaskStatus, User, Project, Task, Integration, Event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime
import uuid


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: UUID) -> Task | None:
        res = await self.db.execute(
            select(Task).where(Task.id == task_id)
        )
        return res.scalar_one_or_none()

    async def list(self) -> list[Task]:
        res = await self.db.execute(select(Task))
        return res.scalars().all()

    async def create_task(
        self,
        project_id: UUID,
        title: str,
        description: str | None = None,
        source: str | None = None,
        external_id: str | None = None,
    ) -> Task:
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            source=source,
            external_id=external_id,
        )
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
    async def create(
        self,
        project_id: UUID,
        title: str,
        description: str | None,
    ) -> Task:
        task = Task(
            id=uuid.uuid4(),
            project_id=project_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(task)
        await self.db.flush()

        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type="TASK_CREATED",
            payload={
                "title": title,
                "description": description,
            },
            created_at=datetime.utcnow(),
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(
        self,
        task: Task,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
    ) -> Task:
        payload = {}

        if title is not None:
            task.title = title
            payload["title"] = title

        if description is not None:
            task.description = description
            payload["description"] = description

        if status is not None:
            task.status = status
            payload["status"] = status.value

        task.updated_at = datetime.utcnow()

        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type="TASK_UPDATED",
            payload=payload,
            created_at=datetime.utcnow(),
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type="TASK_DELETED",
            payload=None,
            created_at=datetime.utcnow(),
        )
        self.db.add(event)

        await self.db.delete(task)
        await self.db.commit()
    
    async def create_or_update_from_external(self, source: str, external_id: str, repo_full_name: str, title: str, description: str) -> Task:
        integration = await self.db.scalar(
            select(Integration)
            .where(Integration.type == source)
            .where(Integration.external_id == repo_full_name)
            .where(Integration.enabled == True)
        )
        if not integration:
            raise ValueError("No enabled integration found for the given source and repository.")
        
        project_id = integration.project_id
        
        q = (
            select(Task)
            .where(Task.source == source)
            .where(Task.external_id == external_id)
        )

        result = await self.db.execute(q)
        task = result.scalar_one_or_none()
        if not task:
            task = await self.create_task(title=title, description=description, source=source, external_id=external_id, project_id=project_id)
            event_type = "TASK_CREATED_FROM_EXTERNAL"
        else:
            task.title = title
            task.description = description
            event_type = "TASK_UPDATED_FROM_EXTERNAL"
        
        await self.db.flush()
        
        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type=event_type,
            payload={
                "source": source,
                "external_id": external_id,
            },
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        
        await self.db.commit()
        return task

    async def update_status_from_external(self, repo_full_name: str, external_id: str, status) -> Task:
        integration = await self.db.scalar(
            select(Integration)
            .where(Integration.type == "github")
            .where(Integration.external_id == repo_full_name)
            .where(Integration.enabled == True)
        )
        if not integration:
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
        await self.db.flush()

        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type="TASK_STATUS_UPDATED_FROM_EXTERNAL",
            payload={"status": status.value},
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        
        await self.db.commit()
        return task
    
    async def delete_task_from_external(self, repo_full_name: str, external_id: str) -> None:
        integration = await self.db.scalar(
            select(Integration)
            .where(Integration.type == "github")
            .where(Integration.external_id == repo_full_name)
            .where(Integration.enabled == True)
        )
        if not integration:
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
        
        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type="TASK_DELETED_FROM_EXTERNAL",
            payload=None,
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        await self.db.flush()
        
        await self.db.delete(task)
        await self.db.commit()

    async def create_or_update_from_google_cal(self, *, project_id: UUID, source: str, external_id: str, title: str, description: str, status: TaskStatus) -> Task:
        q = (
            select(Task)
            .where(Task.source == source)
            .where(Task.external_id == external_id)
            .where(Task.project_id == project_id)
        )

        result = await self.db.execute(q)

        task = result.scalar_one_or_none()

        if task:
            task.title = title
            task.description = description
            task.status = status
        else:
            task = Task(
                project_id=project_id,
                title=title,
                description=description,
                status=status,
                source=source,
                external_id=external_id
            )
            self.db.add(task)
        
        await self.db.flush()
        
        event = Event(
            id=uuid.uuid4(),
            task_id=task.id,
            event_type="google_calendar.sync",
            payload={
                "source": source,
                "external_id": external_id,
            },
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        
        await self.db.commit()
        return task
        
class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, name: str, owner_id: UUID, description: str | None = None) -> Project:
        project = Project(
            id=uuid.uuid4(),
            name=name,
            owner_id=owner_id,
            description=description,
            created_at=datetime.utcnow()
        )
        self.db.add(project)
        try:
            await self.db.commit()
            await self.db.refresh(project)
            return project
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_project_by_id(self, project_id: UUID) -> Project | None:
        try:
            result = await self.db.execute(select(Project).where(Project.id == project_id))
            return result.scalars().first()
        except SQLAlchemyError:
            raise

    async def update_project(self, project_id: UUID, name: str | None = None, description: str | None = None) -> Project:
        project = await self.get_project_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        if name:
            project.name = name
        if description:
            project.description = description
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: UUID) -> None:
        project = await self.get_project_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        await self.db.delete(project)
        await self.db.commit()


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: str) -> User | None:
        try:
            res = await self.db.execute(select(User).where(User.id == user_id))
            user = res.scalars().first()
            return user
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
    
    async def create_user(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: str, username: str | None = None, email: str | None = None) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if username:
            user.username = username
        if email:
            user.email = email

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: str) -> None:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        await self.db.delete(user)
        await self.db.commit()


class IntegrationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: IntegrationCreate) -> Integration:
        integration = Integration(**data.dict())
        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def get_by_id(self, integration_id: UUID) -> Integration | None:
        result = await self.db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID) -> list[Integration]:
        result = await self.db.execute(
            select(Integration).where(Integration.project_id == project_id)
        )
        return result.scalars().all()

    async def get_all(self) -> list[Integration]:
        result = await self.db.execute(
            select(Integration)
        )
        return result.scalars().all()

    async def update(self, integration: Integration, data: IntegrationUpdate) -> Integration:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(integration, key, value)

        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def delete(self, integration: Integration):
        await self.db.delete(integration)
        await self.db.commit()


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, event_id: UUID) -> Event | None:
        res = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        return res.scalar_one_or_none()

    async def get_by_task(self, task_id: UUID) -> list[Event]:
        res = await self.db.execute(
            select(Event)
            .where(Event.task_id == task_id)
            .order_by(Event.created_at.desc())
        )
        return res.scalars().all()
    
    async def get_all(self):
        result = await self.db.execute(select(Event).order_by(Event.created_at.desc()))
        return result.scalars().all()
