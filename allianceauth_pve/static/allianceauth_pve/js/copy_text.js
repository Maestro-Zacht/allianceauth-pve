function copyText(event) {
    const text = event.currentTarget.textContent;
    navigator.clipboard.writeText(text);
    window.alert(text);
}

$(".copy-text").on("click", copyText);