document.addEventListener('DOMContentLoaded', () => {
    const now = new Date();
    document.getElementById('datetime').textContent = now.toLocaleString();

    const search = document.getElementById('search');
    if (search) {
        search.addEventListener('input', () => {
            const keyword = search.value.toLowerCase();
            document.querySelectorAll("tbody tr").forEach(row => {
                const title = row.children[0].textContent.toLowerCase();
                row.style.display = title.includes(keyword) ? '' : 'none';
            });
        });
    }
});

function editEvent(id, title, datetime) {
    document.getElementById('event_id').value = id;
    document.getElementById('title').value = title;
    document.getElementById('datetime_input').value = datetime;
}
