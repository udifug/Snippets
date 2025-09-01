function voteComment(commentId, vote) {
    fetch('/api/comment/like/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
            comment_id: commentId,
            vote: vote
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(`data=${data}`);
        })
        .catch(error => {
            console.error("Error:", error)
        })
        location.reload();
}

