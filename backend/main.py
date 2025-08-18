from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text

# setup the mysql db connection using root and password
engine = create_engine("mysql+pymysql://root:root@localhost:3306/notehub", echo=True)


class NoteIn(BaseModel): # use pydantic to check inputs
    text: str

app = FastAPI() # define fastapi app

@app.on_event("startup") # make a db on startup if it doesn't exist
def startup():
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS notes (id INT AUTO_INCREMENT PRIMARY KEY, text VARCHAR(200) NOT NULL)"))
                            # create table called notes if one doesn't exist w 2 columns, id and text
                            # id is the key, it auto increments and is an int
                            # text is a string between 1 and 200 characters and must contain something

@app.get("/") # root
def root():
    return {"API": "NoteCloud running"}

@app.get("/notes") # get all notes
def list_notes():
    with engine.connect() as conn:  # connect to the db
        return conn.execute(text("SELECT id, text FROM notes")).mappings().all() # mapping() returns dicts and all() gets all results

@app.get("/notes/{note_id}") # get a note by its id
def get_note(note_id: int):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM notes WHERE id = {note_id}"), {"id": note_id}).mappings().fetchone() 
        if not result:
            raise HTTPException(status_code=404, detail="Note not found") # if no result is found error
        return result

@app.post("/notes") # create a new note
def add_note(note: NoteIn): # input is a {text: str}
    with engine.begin() as conn: # begin() commits automatically
        result = conn.execute(text("INSERT INTO notes (text) VALUES (:text)"), {"text": note.text}) # :text acts as placeholder for text input
        new_id = result.lastrowid # get the id of the newly created note
        return {"id": new_id, "text": note.text}

@app.put("/notes/{note_id}") # update an existing note based on its id (ex. /notes/3 would update note with id 3)
def update_note(note_id: int, update: NoteIn): # input is an {note_id: int} and a {text: str}
    with engine.begin() as conn: # use begin() again
        result = conn.execute(text("UPDATE notes SET text = :text WHERE id = :id"), {"text": update.text, "id": note_id}) # use placeholders again
        if result.rowcount == 0: # rowcount is an object from sqlalchemy that tells us how many rows were affected, if it's 0 then nothing happened and an error is raised
            raise HTTPException(status_code=404, detail="Note not found")
        return {"id": note_id, "text": update.text}

@app.delete("/notes/{note_id}") # delete a note
def delete_note(note_id: int):
    with engine.begin() as conn:
        result = conn.execute(text("DELETE FROM notes WHERE id = :id"), {"id": note_id})
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"deleted?": "yeppers"}