let tg = window.Telegram.WebApp;
tg.expand();

document.getElementById('addNoteBtn').addEventListener('click', () => {
    tg.showPopup({
        title: 'Add Note',
        message: 'Enter your note:',
        buttons: [{ type: 'ok', text: 'Add' }]
    }, (buttonId) => {
        if (buttonId === 'ok') {
            // Here you would typically send the note to your server
            alert('Note added!');
        }
    });
});

document.getElementById('viewNotesBtn').addEventListener('click', () => {
    // Here you would typically fetch notes from your server
    let notes = ['Sample note 1', 'Sample note 2'];
    let notesList = document.getElementById('notesList');
    notesList.innerHTML = notes.map(note => `<p>${note}</p>`).join('');
});