async function deleteNote(noteId) {
    try {
        const res = await fetch('/delete-note', {
            method: 'POST',
            body: JSON.stringify({ noteID: noteId }),
            headers: { 'Content-Type': 'application/json' }
        });

        if (!res.ok) {
            console.error('Failed to delete note', res.status);
            return;
        }

        const btn = document.querySelector(`#notes button[onClick*="${noteId}"]`);
        if (btn && btn.parentElement) {
            btn.parentElement.remove();
        } else {
            window.location.reload();
        }
    } catch (err) {
        console.error('Error deleting note:', err);
    }
}

window.deleteNote = deleteNote;