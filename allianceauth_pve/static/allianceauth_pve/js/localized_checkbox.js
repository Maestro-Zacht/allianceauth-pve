function onInput(ev) {
    const value = +ev.currentTarget.value.replaceAll(",", "");
    ev.currentTarget.value = value.toLocaleString('en-GB');
}

$(".localized-input").on("input", onInput);
$(".localized-input").trigger("input");