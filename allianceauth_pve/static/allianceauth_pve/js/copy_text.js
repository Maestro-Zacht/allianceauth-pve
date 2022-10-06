function copyText(event) {
    const text = event.currentTarget.textContent;
    navigator.clipboard.writeText(text);
    window.alert("Copied: " + text);
}

function rowCopied(event) {
    if (event.target.classList.contains("copy-text")) {
        event.currentTarget.classList.add('copied');
    }
}

$(".copy-text").on("click", copyText);
$(".copy-row").on("click", rowCopied);