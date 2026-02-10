from typing import List,Optional
from fastapi import FastAPI,Query
from pydantic import BaseModel,Field
from fastapi import HTTPException
from enum import Enum


app = FastAPI()

todos=[]


class Todo(BaseModel):
    title:str
    completed:bool=False
    tegi: List[str]=Field(default_factory=list)
class Priority(str,Enum):
    low='low'
    medium='medium'
    high='high'

class TodoAndPriority(BaseModel):
    title: str
    completed: bool = False
    priority: Priority = Priority.medium
    tegi: List[str]=Field(default_factory=list)
class SortOrder(str, Enum):
    asc = 'asc'
    desc = 'desc'

@app.get('/todos', response_model=List[TodoAndPriority])
def get_todos(priority:Optional[Priority]=Query(None,description='Фильтр по приоритету'),SortTegi:Optional[str]=Query(None,description='Поиск по тегу'),sort_by: Optional[str] = Query("priority", description="Поле для сортировки"),order: SortOrder = Query(SortOrder.asc, description="Порядок сортировки")):
    filter_tasks=todos.copy()
    if priority:
        filter_tasks=[task for task in filter_tasks if task.priority==priority]
    if SortTegi:
        filter_tasks=[task for task in filter_tasks if SortTegi in task.tegi]
    if sort_by == "priority":
        priority_order = {
            Priority.low: 1,
            Priority.medium: 2,
            Priority.high: 3
        }
        filter_tasks.sort( key=lambda x:priority_order[x.priority],
        reverse=(order==SortOrder.desc)
                          )
    return filter_tasks


@app.post('/todos')
def create_todo(todo:Todo,priority:Priority):
    todo_with_priorety=TodoAndPriority(
        title=todo.title,
        completed=todo.completed,
        priority=priority,
        tegi=todo.tegi
    )
    todos.append(todo_with_priorety)
    if priority == Priority.low:
        return {'message': 'Todo created', 'id': len(todos)-1,'low': priority.value}
    if priority == Priority.medium:
        return {'message': 'Todo created', 'id': len(todos) - 1, 'medium': priority.value}
    return {'message': 'Todo created', 'id': len(todos) - 1, 'high': priority.value}

@app.get('/todos/{todo_id}')
def get_todo(todo_id: int):
    if todo_id>=len(todos):
        raise HTTPException(status_code=404,detail='Todo not found')
    return todos[todo_id]

@app.delete('/todos/{todo_id}')
def delete_todo(todo_id: int):
    if todo_id>=len(todos):
        raise HTTPException(status_code=404,detail='Todo not found')
    deleted=todos.pop(todo_id)
    return {'message':'Todo deleted', 'todo':deleted}

