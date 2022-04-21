const addBtn = document.getElementById('search-bar-btn');
const usersContainer = document.getElementById('users');
const searchBar = document.getElementById('search-bar-id');
const searchResults = document.getElementById('search-results');
let totalForms = document.querySelector("#id_form-TOTAL_FORMS");
let formNum = totalForms.getAttribute('value');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


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

const zeroCharacter = { profilePic: '', username: '', userId: 0, setup: false, count: 1 };

function addCharacter(initial) {
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
    name.type = "number";
    name.setAttribute('value', data.userId);
    name.name = `form-${formNum}-user`;
    name.id = `id_form-${formNum}-user`;
    name.readOnly = true;
    name.style.display = 'none';
    name.classList.add("user-pk-list");

    const profileDiv = document.createElement('div');
    profileDiv.id = `profile-div-${formNum}`;

    const profilePic = document.createElement('img');
    profilePic.src = data.profilePic;
    profilePic.id = `profile-pic-${formNum}`;
    profilePic.classList.add('img-circle');
    profilePic.style.marginRight = "1rem";

    const userSpan = createSpan(data.username);
    userSpan.id = `username-span-${formNum}`;
    userSpan.style.marginLeft = "20px"

    profileDiv.appendChild(profilePic);
    profileDiv.appendChild(userSpan);

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
    count.style.width = "10ch";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.classList.add('btn', 'btn-danger');
    deleteButton.id = `delete-row-${formNum}`;
    deleteButton.style.transform = "scale(0.5, 0.5)";

    const deleteImage = document.createElement('i');
    deleteImage.classList.add('fa', 'fa-times');
    deleteImage.id = `delete-icon-${formNum}`;

    deleteButton.appendChild(deleteImage);

    usersContainer.append(name, profileDiv, check, count, deleteButton);

    formNum++;
    totalForms.setAttribute('value', `${formNum}`);
}

function removeCharacter(index) {
    let dataCopy = [];

    for (let i = 0; i < formNum; i++) {
        if (i != index) {
            dataCopy.push({
                userId: document.getElementById(`id_form-${i}-user`).value,
                username: document.getElementById(`username-span-${i}`).textContent,
                profilePic: document.getElementById(`profile-pic-${i}`).src,
                setup: document.getElementById(`id_form-${i}-helped_setup`).checked,
                count: document.getElementById(`id_form-${i}-share_count`).value
            })
        }
        document.getElementById(`id_form-${i}-user`).remove();
        document.getElementById(`username-span-${i}`).remove();
        document.getElementById(`profile-pic-${i}`).remove();
        document.getElementById(`profile-div-${i}`).remove();
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

    let excludeIds = [];
    let queryStr = '';

    Array.from(usersContainer.getElementsByClassName('user-pk-list')).forEach((el) => {
        excludeIds.push(el.getAttribute('value'));
    });

    if (excludeIds.length > 0) {
        queryStr = '?excludeIds=' + excludeIds.join('&excludeIds=');
    } else {
        queryStr = '';
    }

    const request = new Request((searchBar.value != '' ? `/pve/ratters/${searchBar.value}/` : '/pve/ratters/') + queryStr, { headers: { 'X-CSRFToken': csrftoken } })
    fetch(request,
        {
            method: "GET",
            credentials: "same-origin",
        }
    ).then(res => {
        res.json().then(data => {
            let results = [];
            data.result.forEach((value, index, array) => {
                const profile_image = document.createElement('img');
                profile_image.src = value.profile_pic;
                profile_image.classList.add('img-circle');
                profile_image.style.marginRight = "1rem";

                let characterInfo = createSpan(value.character_name);

                let addButton = document.createElement('button');
                addButton.textContent = "Add";
                addButton.type = "button";
                addButton.classList.add('btn', 'btn-success');
                addButton.addEventListener('click', () => {
                    addCharacter({ profilePic: value.profile_pic, userId: value.user_id, username: value.character_name, setup: false, count: 1 });
                    searchResults.replaceChildren(createSpan('No results', 'all-cols head'));
                    searchBar.value = '';
                })


                results.push(profile_image, characterInfo, addButton);
            })
            searchResults.replaceChildren(...results);
        })
    })
});

usersContainer.addEventListener('click', e => {
    if (e.target && (e.target.matches('button') || e.target.matches('i'))) {
        let buttonId = parseInt(e.target.id.match(/[0-9]+/g)[0]);
        removeCharacter(buttonId);
    }
})