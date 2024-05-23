from fastapi import FastAPI, Request
import sqlite3 as sql
import random
import string

app = FastAPI()
conn = sql.connect("todo.db", check_same_thread=False)
todoModel = ["todoId", "todoContent", "isDone", "todoCreated", "userId", "taskOwner"]

@app.get("/")
def index():
    return { "msg": "Hello world" }

@app.get("/todos/{id}")
def todos(id: str):
    with conn as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM todos WHERE userId=?", (id,))
        con.commit()
        todos = cur.fetchall()
        cur.execute("SELECT * FROM shared WHERE userId=?", (id,))
        con.commit()
        sharedtodos = cur.fetchall()
        print(todos.reverse())
        print(sharedtodos.reverse())
        todosJson = []
        for todo in todos:
            todosJson.append( { k:v for (k,v) in zip(todoModel, todo) } )
        for shared in sharedtodos:
            todosJson.append( { k:v for (k,v) in zip(todoModel, shared) } )
    return { "todos": todosJson }
        
@app.get("/getcode")
def getcode():
    while True:
        usercode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        with conn as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE userId=?", (usercode,))
            con.commit()
            checkCode = cur.fetchall()
        if len(checkCode)>0:
            pass
        else:
            break
    return { "usercode": usercode }

@app.post("/loginuser")
async def test(request: Request):
    data = await request.json()
    usercode = data["usercode"]
    with conn as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE userId=?", (usercode,))
        con.commit()
        result = cur.fetchall()
    if len(result)>0:
        return { "message": "user found", "welcome": result[0][1] }
    else:
        return { "message": "user not found" }

@app.post("/registeruser")
async def registeruser(request: Request):
    data = await request.json()
 
    username = data["username"]
    usercode = data["usercode"]
    usercreated = data["usercreated"]

    with conn as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES (?,?,?)", (usercode, username, usercreated))
        con.commit()
 
    return {"message": "User data submitted successfully!"}

@app.post("/addtodo")
async def addtodo(request: Request):
    data = await request.json()
    
    while True:
        todoid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        with conn as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM todos WHERE userId=?", (todoid,))
            con.commit()
            checkCode = cur.fetchall()
        if len(checkCode)>0:
            pass
        else:
            break
    todocontent = data["todocontent"]
    isdone = int(data["isdone"])
    todocreated = data["todocreated"]
    userid = data["userid"]

    with conn as con:
        cur = con.cursor()
        cur.execute("SELECT userName FROM users WHERE userId=?", (userid,))
        con.commit()
        username = cur.fetchone()
        cur.execute("INSERT INTO todos VALUES (?,?,?,?,?,?,?)", (todoid, todocontent, isdone, todocreated, userid, username[0], 1))
        con.commit()
        
    return {"message": "todo has been added"}

@app.post("/addtodowithcode")
async def addtodowithcode(request: Request):
    data = await request.json()
    
    while True:
        sharedid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        with conn as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM shared WHERE sharedId=?", (sharedid,))
            con.commit()
            checkCode = cur.fetchall()
        if len(checkCode)>0:
            pass
        else:
            break
    todoid = data["todoid"]
    isdone = int(data["isdone"])
    todocreated = data["todocreated"]
    userid = data["userid"]

    with conn as con:
        cur = con.cursor()
        cur.execute("SELECT todoContent, taskOwner FROM todos WHERE todoId=? AND isOriginal=?", (todoid,1))
        con.commit()
        todoinfo = cur.fetchone()
        cur.execute("INSERT INTO todos VALUES (?,?,?,?,?,?,?)", (sharedid, todoinfo[0], isdone, todocreated, userid, todoinfo[1], 0))
        con.commit()
        
    return {"message": "todo has been added"}

@app.put("/donetodo")
async def donetodo(request: Request):
    data = await request.json()
    
    todoid = data["todoid"]

    with conn as con:
        cur = con.cursor()
        cur.execute("UPDATE todos SET isDone=1 WHERE todoId=?", (todoid,))
        con.commit()
        
    return {"message": "todo has been added"}

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application using uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
