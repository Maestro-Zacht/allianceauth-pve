const decimal_separators_re = /[\D\s_\.\-]/g;

function onInput(ev) {
    const value = +ev.currentTarget.value.replace(decimal_separators_re, "");
    ev.currentTarget.value = value.toLocaleString();
}

$(".localized-input").on("input", onInput);
$(".localized-input").trigger("input");