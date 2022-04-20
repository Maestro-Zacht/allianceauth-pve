const addBtn = document.getElementById('new-share');
const usersContainer = document.getElementById('users');
const rowBlueprint = document.getElementById('share-form-blueprint');
let totalForms = document.querySelector("#id_form-TOTAL_FORMS");
let formNum = totalForms.getAttribute('value');


function initObj(src, def) {
    if (!src) return Object.assign({}, def);
    const res = {};
    for (var key in def) {
        res[key] = key in src ? src[key] : def;
    }
    return res;
}

function createSpan(text, className = "") {
    const span = document.createElement("span");
    if (className) span.className = className;
    span.textContent = text;
    return span;
}


function addCharacter() {
    if (formNum == 0) {
        usersContainer.textContent = '';
        usersContainer.append(
            createSpan("Character", "head"),
            createSpan("Setup", "head"),
            createSpan("Count", "head")
        );
    }

    // username
    const name = document.createElement("input");
    name.type = "text";
    name.value = '';
    name.name = `form-${formNum}-user`;
    name.id = `id_form-${formNum}-user`;
    name.setAttribute('list', 'characters');

    // setup
    const check = document.createElement("input");
    check.type = "checkbox";
    check.checked = false;
    check.classList.add("setup");
    check.name = `form-${formNum}-helped_setup`;
    check.id = `id_form-${formNum}-helped_setup`;
    const count = document.createElement("input");
    count.type = "number";
    count.name = `form-${formNum}-share_count`;
    count.min = "0";
    count.id = `id_form-${formNum}-share_count`;

    usersContainer.append(name, check, count);

    formNum++;

    totalForms.setAttribute('value', `${formNum}`);
}

function removeCharacter(index) {
    if (index < 0 || elements.length <= index) return;
    const el = elements[index];
    console.log(el);
    el[0].remove();
    el[1].remove();
    el[2].remove();
    elements.splice(index, 1);
}

addBtn.addEventListener("click", () => addCharacter());