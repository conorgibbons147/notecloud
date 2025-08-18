from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# building a test API without the database for now just to get the endpoints and concepts down, will translate to mysql db using docker in main.py

app = FastAPI()

# for now just store notes in memory before setting up a db
NOTES = []
NEXT_ID = 1

class NoteIn(BaseModel): # using pydantic base model here to make sure the text input of a note is a str
    text: str

@app.get("/") # root endpoint
def root():
    return {"API": "NoteCloud is running"}

@app.get("/notes") # shows us all the notes
def list_notes(): 
    return NOTES

@app.post("/notes") # adds a new note
def add_note(note: NoteIn): # checks to see if the note is valid under NoteIn
    global NEXT_ID
    new = {"id": NEXT_ID, "text": note.text} # create a new note with an id
    NOTES.append(new) # add note to the list (currently the db)
    NEXT_ID += 1 # move onto next note id so new notes get new ids
    return new # return the new note

@app.delete("/notes/{note_id}") # deletes a note based on note id
def delete_note(note_id: int): # gets id and passes it as an int into the function
    for i, n in enumerate(NOTES): # loop through the existing notes
        if n["id"] == note_id: # if the id matches the id that we want to delete
            NOTES.pop(i) # remove the note from the list
            return {"ok": True} # and return that it worked
    raise HTTPException(status_code=404, detail="Note not found") # if id not found give this error using HTTPException

@app.post("/notes/{note_id}") # updates a note based on note id
def update_notes(note_id: int, note: NoteIn): # gets id and the new note text
    for i, n in enumerate(NOTES): # loop through the existing notes
        if n["id"] == note_id: # if id matches
            NOTES[i] = {"id": note_id, "text": note.text} # note will be new note with same id
            return NOTES[i] # return updated note
    raise HTTPException(status_code=404, detail="Note not found")  # error if note not found

@app.get("/notes/{note_id}") # gets a specific note based on note id
def get_note(note_id: int): # gets id and passes it as an int into the function
    for n in NOTES: # loop through the existing notes
        if n["id"] == note_id: # if id matches
            return n # return the note
    raise HTTPException(status_code=404, detail="Note not found")
