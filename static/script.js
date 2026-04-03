function sendGuess() {
    let guess = document.getElementById("guess").value;

    fetch("/guess", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ guess: guess })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = data.result;
    });
}