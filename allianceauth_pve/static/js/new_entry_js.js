const searchBtn = document.getElementById('search-bar-btn');
const usersContainer = document.getElementById('users');
const searchBar = document.getElementById('search-bar-id');
const searchResults = document.getElementById('search-results');
let totalForms = document.querySelector("#id_form-TOTAL_FORMS");
let formNum = totalForms.getAttribute('value');
const incrementAllButton = document.getElementById('incrementAllButton');
const incrementSelectedButton = document.getElementById('incrementSelectedButton');
const decrementSelectedButton = document.getElementById('decrementSelectedButton');
const decrementAllButton = document.getElementById('decrementAllButton');
const estimatedTotalInput = document.getElementById('id_estimated_total');

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
        res[key] = key in src ? src[key] : def[key];
    }
    return res;
}

function createSpan(text, className = "") {
    const span = document.createElement("span");
    if (className) span.className = className;
    span.textContent = text;
    return span;
}

const zeroCharacter = { profilePic: '', username: '', userId: 0, setup: false, count: 1, selected: true };

function addCharacter(initial) {
    const data = initObj(initial, zeroCharacter);
    if (formNum == 0) {
        usersContainer.textContent = '';
        usersContainer.append(
            createSpan("Select", "head"),
            createSpan("Character", "head"),
            createSpan("Setup", "head"),
            createSpan("Count", "head"),
            createSpan("Delete", "head"),
        );
    }

    const userSelectedInput = document.createElement('input');
    userSelectedInput.type = "checkbox";
    userSelectedInput.classList.add('setup');
    userSelectedInput.id = `select-share-checkbox-${formNum}`;
    userSelectedInput.checked = data.selected;

    const userCheckedIcon = document.createElement('i');
    userCheckedIcon.classList.add('fas', 'fa-arrow-right', 'checked', 'selected-user');

    const userUncheckedIcon = document.createElement('i');
    userUncheckedIcon.classList.add('fas', 'fa-running', 'unchecked', 'unselected-user');

    const userSelectedLabel = document.createElement('label');
    userSelectedLabel.htmlFor = userSelectedInput.id;
    userSelectedLabel.classList.add('custom-checkbox');
    userSelectedLabel.id = `select-share-label-${formNum}`;
    userSelectedLabel.appendChild(userSelectedInput);
    userSelectedLabel.appendChild(userCheckedIcon);
    userSelectedLabel.appendChild(userUncheckedIcon);

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

    const checkLabel = document.createElement('label');
    checkLabel.htmlFor = check.id;
    checkLabel.id = `helped_setup-label-${formNum}`;
    checkLabel.classList.add('custom-checkbox', 'red-heart');

    const uncheckedIcon = document.createElement('i');
    uncheckedIcon.classList.add('far', 'fa-heart', 'unchecked');

    const checkedIcon = document.createElement('i');
    checkedIcon.classList.add('fas', 'fa-heart', 'checked');

    checkLabel.appendChild(check);
    checkLabel.appendChild(checkedIcon);
    checkLabel.appendChild(uncheckedIcon);

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
    deleteButton.addEventListener('click', (el) => {
        removeCharacter(el.currentTarget.id.match(/[0-9]+/g)[0]);
    })

    const deleteImage = document.createElement('i');
    deleteImage.classList.add('fa', 'fa-times');
    deleteImage.id = `delete-icon-${formNum}`;

    deleteButton.appendChild(deleteImage);

    usersContainer.append(userSelectedLabel, name, profileDiv, checkLabel, count, deleteButton);

    formNum++;
    totalForms.setAttribute('value', `${formNum}`);
}

function removeCharacter(index) {
    let dataCopy = [];

    for (let i = 0; i < formNum; i++) {
        if (i != index) {
            dataCopy.push({
                selected: document.getElementById(`select-share-checkbox-${i}`).checked,
                userId: document.getElementById(`id_form-${i}-user`).value,
                username: document.getElementById(`username-span-${i}`).textContent,
                profilePic: document.getElementById(`profile-pic-${i}`).src,
                setup: document.getElementById(`id_form-${i}-helped_setup`).checked,
                count: document.getElementById(`id_form-${i}-share_count`).value
            })
        }
        document.getElementById(`select-share-label-${i}`).remove();
        document.getElementById(`id_form-${i}-user`).remove();
        document.getElementById(`username-span-${i}`).remove();
        document.getElementById(`profile-pic-${i}`).remove();
        document.getElementById(`profile-div-${i}`).remove();
        document.getElementById(`helped_setup-label-${i}`).remove();
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

function addToUserCount(index, value) {
    if (index >= 0 && index < formNum) {
        const count = document.getElementById(`id_form-${index}-share_count`);
        if (parseInt(count.value) + value >= 0) {
            count.stepUp(value);
        }
    }
}

function isUserSelected(index) {
    if (index >= 0 && index < formNum) {
        const userCheckbox = document.getElementById(`select-share-checkbox-${index}`);
        return userCheckbox ? userCheckbox.checked : false;
    } else {
        return false;
    }
}

function incrementEstimatedTotal(value) {
    let newValue = +estimatedTotalInput.value + value;
    if (newValue > 0 && newValue < +estimatedTotalInput.max) {
        estimatedTotalInput.value = newValue;
    }
}

searchBtn.addEventListener("click", e => {
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
                    addCharacter({ profilePic: value.profile_pic, userId: value.user_id, username: value.character_name });
                    searchResults.replaceChildren(createSpan('No results', 'all-cols head'));
                    searchBar.value = '';
                })


                results.push(profile_image, characterInfo, addButton);
            })
            searchResults.replaceChildren(...results);
        })
    })
});

incrementAllButton.addEventListener('click', () => {
    for (let i = 0; i < formNum; i++) {
        addToUserCount(i, 1);
    }
});

decrementAllButton.addEventListener('click', () => {
    for (let i = 0; i < formNum; i++) {
        addToUserCount(i, -1);
    }
});

incrementSelectedButton.addEventListener('click', () => {
    for (let i = 0; i < formNum; i++) {
        if (isUserSelected(i)) {
            addToUserCount(i, 1);
        }
    }
});

decrementSelectedButton.addEventListener('click', () => {
    for (let i = 0; i < formNum; i++) {
        if (isUserSelected(i)) {
            addToUserCount(i, -1);
        }
    }
});