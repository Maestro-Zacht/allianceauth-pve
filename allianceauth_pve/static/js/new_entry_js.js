const addBtn = document.getElementById('search-bar-btn');
const usersContainer = document.getElementById('users');
const searchBar = document.getElementById('search-bar-id');
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

const zeroCharacter = { user: '', setup: false, count: 1 };

function addCharacter(initial = null) {
    const data = initObj(initial, zeroCharacter);
    if (formNum == 0) {
        usersContainer.textContent = '';
        usersContainer.append(
            createSpan("Character", "head"),
            createSpan("Setup", "head"),
            createSpan("Count", "head"),
            createSpan("Delete", "head"),
        );
    }

    const name = document.createElement("input");
    name.type = "text";
    name.value = data.user;
    name.name = `form-${formNum}-user`;
    name.id = `id_form-${formNum}-user`;
    name.setAttribute('list', 'characters');
    name.readOnly = true;

    const check = document.createElement("input");
    check.type = "checkbox";
    check.checked = data.setup;
    check.classList.add("setup");
    check.name = `form-${formNum}-helped_setup`;
    check.id = `id_form-${formNum}-helped_setup`;

    const count = document.createElement("input");
    count.type = "number";
    count.name = `form-${formNum}-share_count`;
    count.min = "0";
    count.id = `id_form-${formNum}-share_count`;
    count.value = data.count;

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.classList.add('btn', 'btn-danger');
    deleteButton.id = `delete-row-${formNum}`;

    const deleteImage = document.createElement('i');
    deleteImage.classList.add('fa', 'fa-times');
    deleteImage.id = `delete-icon-${formNum}`;

    deleteButton.appendChild(deleteImage);

    usersContainer.append(name, check, count, deleteButton);

    formNum++;
    totalForms.setAttribute('value', `${formNum}`);
}

function removeCharacter(index) {
    let dataCopy = [];

    for (let i = 0; i < formNum; i++) {
        if (i != index) {
            dataCopy.push({
                user: document.getElementById(`id_form-${i}-user`).value,
                setup: document.getElementById(`id_form-${i}-helped_setup`).checked,
                count: document.getElementById(`id_form-${i}-share_count`).value
            })
        }
        document.getElementById(`id_form-${i}-user`).remove();
        document.getElementById(`id_form-${i}-helped_setup`).remove();
        document.getElementById(`id_form-${i}-share_count`).remove();
        document.getElementById(`delete-row-${i}`).remove();
    }

    formNum = 0;
    totalForms.setAttribute('value', `${formNum}`);
    if (formNum == 0) {
        usersContainer.replaceChildren(createSpan("No character yet", "all-cols head"));
    }

    dataCopy.forEach((value, index, array) => {
        addCharacter(value);
    })
}

addBtn.addEventListener("click", e => {
    e.preventDefault()
    const data = { user: searchBar.value, setup: false, count: 1 };
    searchBar.value = '';
    addCharacter(data);
});

usersContainer.addEventListener('click', e => {
    if (e.target && (e.target.matches('button') || e.target.matches('i'))) {
        let buttonId = parseInt(e.target.id.match(/[0-9]+/g)[0]);
        removeCharacter(buttonId);
    }
})