function copyText(event) {
    const text = event.currentTarget.textContent;
    navigator.clipboard.writeText(text);
    spop({
        template: "Copied: " + text,
        style: "info",
        autoclose: 5000,
        position: 'bottom-right',
    });
}

function toggleRow(event) {
    if (event.target.classList.contains("copy-text")) {
        event.currentTarget.classList.add('copied');
    } else if (event.target.classList.contains("undo-copy")) {
        event.currentTarget.classList.remove('copied');
    }
}

$(".copy-text").on("click", copyText);
$(".copy-row").on("click", toggleRow);