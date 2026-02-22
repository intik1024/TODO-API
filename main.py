from typing import List,Optional
from fastapi import FastAPI,Query,Body
from pydantic import BaseModel,Field
from fastapi import HTTPException
from enum import Enum
from datetime import date


app = FastAPI()

todos=[]


class Todo(BaseModel):
    title:str
    completed:bool=False
    tegi: List[str]=Field(default_factory=list)
    due_date: Optional[date]=None
class Priority(str,Enum):
    low='low'
    medium='medium'
    high='high'

class TodoAndPriority(BaseModel):
    title: str
    completed: bool = False
    priority: Priority = Priority.medium
    tegi: List[str]=Field(default_factory=list)
    due_date: Optional[date]=None
class SortOrder(str, Enum):
    asc = 'asc'
    desc = 'desc'
@app.get('/todos/expering_date')
def expering_date():
    today=date.today()
    exp_date=[]
    for task in todos:
        if task.due_date and task.due_date<today:
            exp_date.append(task)
    return exp_date

@app.get('/todos/grouped')
def SearchTegis():
    grouded={}
    for task in todos:
         for tag in task.tegi:
             if tag not in grouded:
                 grouded[tag]=[]
             grouded[tag].append(task)
    return grouded

@app.get('/todos', response_model=List[TodoAndPriority])
def get_todos(priority:Optional[Priority]=Query(None,description='Фильтр по приоритету'),SortTegi:Optional[str]=Query(None,description='Поиск по тегу'),sort_by: Optional[str] = Query("priority", description="Поле для сортировки"),order: SortOrder = Query(SortOrder.asc, description="Порядок сортировки"),skip:int = Query(0,ge=0,description='Сколько задач пропустить'),limit:int=Query(10,ge=1,le=100,description='Сколько задач вернуть'),SortBool:bool=Query(None,description='Какие задачивывести')):
    filter_tasks=todos.copy()

    if priority:
        filter_tasks=[task for task in filter_tasks if task.priority==priority]
    if SortTegi:
        filter_tasks=[task for task in filter_tasks if SortTegi in task.tegi]
    if SortBool is not None:
        filter_tasks=[task for task in filter_tasks if task.completed ==SortBool]
    if sort_by == "priority":
        priority_order = {
            Priority.low: 1,
            Priority.medium: 2,
            Priority.high: 3
        }
        filter_tasks.sort( key=lambda x:priority_order[x.priority],
        reverse=(order==SortOrder.desc)
                          )
    elif sort_by=='due_date':
        filter_tasks.sort(key=lambda x: (x.due_date is None,x.due_date),
                          reverse=(order==SortOrder.desc))
    paginat_tasks=filter_tasks[skip:skip+limit]
    return paginat_tasks
@app.get('/todos/sort')
def Sorttirovka():
    if len(todos)==0:
        return {'message':'нет задач'}
    c=0
    for task in todos:
        if task.completed:
            c+=1
    total=len(todos)
    percentage=(c/total)*100
    l=0
    m=0
    h=0
    for prior in todos:
        if prior.priority==Priority.low:
            l+=1
        elif prior.priority==Priority.medium:
            m+=1
        else:
            h+=1
    return {'percentage of completed tasks':percentage,'number of low priority tasks':l,'number of medium priority tasks':m,'number of high priority tasks':h}
@app.post('/todos')
def create_todo(todo:Todo,priority:Priority):
    todo_with_priorety=TodoAndPriority(
        title=todo.title,
        completed=todo.completed,
        priority=priority,
        tegi=todo.tegi,
        due_date=todo.due_date
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
@app.patch('/todos/{todo_id}')
def update_completed (todo_id:int,completed:bool=Body(...,embed=True)):
    if todo_id>=len(todos):
        raise HTTPException(status_code=404,detail='Todo not found')
    todos[todo_id].completed=completed
    return {'message' :f'todo update to {completed}',
            'todo':todos[todo_id]
    }


