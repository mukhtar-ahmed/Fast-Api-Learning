from fastapi import FastAPI, HTTPException, Query , Path, Body
from pydantic import BaseModel, Field
from starlette import status
app = FastAPI()

class Employee:
    id:int
    name:str
    age:int
    department:str
    
    def __init__(self,id,name,age,department):
        self.id = id
        self.name= name
        self.age = age
        self.department = department
class EmployeeIn(BaseModel):
    id:int
    name:str= Field(min_length=2, max_length=50)
    age:int = Field(gt=0)
    department:str = Field(min_length=1)
    
    model_config = {
        'json_schema_extra':
            {
                "example":{
                    "id":1,
                    "name":"John",
                    "age":30,
                    "department":"IT"
                }
            }
    }
        
employees = [
    Employee(1, "John", 25, "Sales"),
    Employee(2, "Jane", 30, "Marketing"),
    Employee(3, "Bob", 35, "IT"),
    Employee(4, "Bob2", 40, "IT"),
]

@app.get('/employees', status_code=status.HTTP_200_OK)
async def all_employees():
    return {
        'total':len(employees),
        'employees':employees
    }
    
@app.get('/employees/', status_code=status.HTTP_200_OK)
async def get_employee_by_department(department:str):
    return_employee = []
    for i in range(len(employees)):
        if employees[i].departement.casefold() == department.casefold():
            return_employee.append(employees[i])
    if len(return_employee) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No Employee found in '{department}' departement"
        )
    return {
        'total': len(return_employee),
        'employees': return_employee
    }
    
@app.get('/employees/{id}', status_code=status.HTTP_200_OK)
async def get_employee_by_id(id:int = Path(gt=0)):
    for i in range(len(employees)):
        if employees[i].id == id:
            return {
                'message':'Employee Found',
                'data':employees[i]
            }
            break
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee Not found"
    )
    
@app.post('/employees/', status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeIn):
    for i in range(len(employees)):
        if (employee.model_dump())['id'] == employees[i].id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Employee already exists"
                )
            break
    employees.append(Employee(**employee.model_dump()))
    return {
        'message':'Employee Created',
        'data':employee
        }
            
@app.put('/employees/{id}/', status_code=status.HTTP_200_OK)
async def update_employee(employee: EmployeeIn,id:int= Path(gt=0)):
    for i in range(len(employees)):
        if employees[i].id == id:
            if (employee.model_dump())['id'] == employees[i].id:
                employees[i] = Employee(**employee.model_dump())
                return {
                    'message':'Employee Updated',
                    'data':employee
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="ID cannot be updated"
                    )
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee Not found"
            )
    
@app.delete('/employees/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(id:int = Path(gt=0)):
    for i in range(len(employees)):
        if employees[i].id == id:
            del employees[i]
            return {
                'message':'Employee Deleted',
                }
            break
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee Not found"
            )
        