from fastapi import APIRouter, HTTPException
from schemas.notes import Note, NoteResponse

router = APIRouter()

notes_counter: int = 0
notes_database: dict = {}

@router.post("/notes", response_model=NoteResponse)
async def create_new_note(note: Note):
    global notes_counter
    notes_counter += 1
    new_note = {
        "id": notes_counter,
        "title": note.title,
        "content": note.content
    }
    notes_database[notes_counter] = new_note
    return new_note

@router.get("/notes", response_model=list[NoteResponse])
async def return_all_notes():
    return list(notes_database.values())

@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_specific_note(note_id: int):
    if note_id not in notes_database:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} does not exist."
        )
    return notes_database[note_id]

@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_new_note(note_id: int, note: Note):
    if note_id not in notes_database:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} does not exist."
        )
    notes_database[note_id].update({
        "title": note.title,
        "content": note.content
    })
    return notes_database[note_id]

@router.delete("/notes/{note_id}")
async def delete_specific_note(note_id: int):
    if note_id not in notes_database:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} does not exist."
        )
    del notes_database[note_id]
    return {"message": f"Note {note_id} has been deleted successfully."}




