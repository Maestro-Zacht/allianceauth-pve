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
let totalRoleForms = document.querySelector("#id_roles-TOTAL_FORMS");
let rolesFormNum = totalRoleForms.getAttribute('value');
const rolesContainer = document.getElementById('roles-div');
const submitRoleButton = document.getElementById('submitNewRoleButton');
const customIncrementButton = document.getElementById('custom_increment_button');
const customIncrementInput = document.getElementById('custom_increment_inp');
const roleSet = new Set();

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

const zeroCharacter = { profilePic: '', username: '', userId: 0, characterPic: '', characterName: '', characterId: 0, setup: false, count: 1, selected: true, role: null };

function addCharacter(initial) {
    const data = initObj(initial, zeroCharacter);
    if (formNum == 0) {
        usersContainer.textContent = '';
        usersContainer.append(
            createSpan("Select", "head"),
            createSpan("User's Main Char", "head"),
            createSpan("Character", "head"),
            createSpan("Role", "head"),
            createSpan("Setup", "head"),
            createSpan("Count", "head"),
            createSpan("Delete", "head"),
        );
    }
    // Selected row
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

    // User
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
    userSpan.style.marginLeft = "5px";

    profileDiv.appendChild(profilePic);
    profileDiv.appendChild(userSpan);

    // Character
    const charname = document.createElement('input');
    charname.type = 'number';
    charname.setAttribute('value', data.characterId);
    charname.name = `form-${formNum}-character`;
    charname.id = `id_form-${formNum}-character`;
    charname.readOnly = true;
    charname.style.display = 'none';
    charname.classList.add('character-pk-list');

    const characterDiv = document.createElement('div');
    characterDiv.id = `character-div-${formNum}`;

    const characterPic = document.createElement('img');
    characterPic.src = data.characterPic;
    characterPic.id = `character-pic-${formNum}`;
    characterPic.classList.add('img-circle');
    characterPic.style.marginRight = "1rem";

    const characterSpan = createSpan(data.characterName);
    characterSpan.id = `character_name-span-${formNum}`;
    characterSpan.style.marginLeft = "5px";

    characterDiv.appendChild(characterPic);
    characterDiv.appendChild(characterSpan);

    // Fleet role
    const fleetRole = document.createElement('select');
    fleetRole.name = `form-${formNum}-role`;
    fleetRole.classList.add('form-control');
    fleetRole.style.height = 'auto';
    fleetRole.id = `id_form-${formNum}-role`;
    for (let i = 0; i < rolesFormNum; i++) {
        const role = document.getElementById(`roles_form-${i}-name_span`);
        const roleOption = document.createElement('option');
        roleOption.text = role.textContent;
        roleOption.value = role.textContent;
        if (role.textContent == data.role) {
            roleOption.selected = true;
        }
        fleetRole.options.add(roleOption);
    }

    // Helped setup
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

    // Site count
    const count = document.createElement("input");
    count.type = "number";
    count.name = `form-${formNum}-site_count`;
    count.min = "0";
    count.id = `id_form-${formNum}-site_count`;
    count.value = data.count;
    count.style.width = "10ch";

    // Delete button
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

    usersContainer.append(userSelectedLabel, name, profileDiv, charname, characterDiv, fleetRole, checkLabel, count, deleteButton);

    formNum++;
    totalForms.setAttribute('value', `${formNum}`);
}

function removeCharacter(index) {
    let dataCopy = [];

    for (let i = 0; i < formNum; i++) {
        if (i != index) {
            const roleSelect = document.getElementById(`id_form-${i}-role`);
            dataCopy.push({
                selected: document.getElementById(`select-share-checkbox-${i}`).checked,
                userId: document.getElementById(`id_form-${i}-user`).value,
                username: document.getElementById(`username-span-${i}`).textContent,
                profilePic: document.getElementById(`profile-pic-${i}`).src,
                characterId: document.getElementById(`id_form-${i}-character`).value,
                characterPic: document.getElementById(`character-pic-${i}`).src,
                characterName: document.getElementById(`character_name-span-${i}`).textContent,
                role: roleSelect.item(roleSelect.selectedIndex).text,
                setup: document.getElementById(`id_form-${i}-helped_setup`).checked,
                count: document.getElementById(`id_form-${i}-site_count`).value,
            })
        }
    }

    formNum = 0;
    totalForms.setAttribute('value', `${formNum}`);
    usersContainer.replaceChildren(createSpan("No character yet", "all-cols head"));

    dataCopy.forEach((value, index, array) => {
        addCharacter(value);
    })
}

function addToUserCount(index, value) {
    if (index >= 0 && index < formNum) {
        const count = document.getElementById(`id_form-${index}-site_count`);
        if (+count.value + value >= 0) {
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
    let newValue = estimatedTotalInput.value.replaceAll(',', "");
    newValue = +newValue + +value;
    if (
        newValue > +estimatedTotalInput.attributes.minvalue.value &&
        newValue < +estimatedTotalInput.attributes.maxvalue.value
    ) {
        estimatedTotalInput.value = newValue;
        estimatedTotalInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

const zeroRole = { name: 'Krab', value: 1 };
function addRole(initial) {
    const data = initObj(initial, zeroRole);

    if (!roleSet.has(data.name)) {
        const nameInput = document.createElement('input');
        nameInput.type = 'hidden';
        nameInput.name = `roles-${rolesFormNum}-name`;
        nameInput.value = data.name;
        nameInput.id = `id_roles-${rolesFormNum}-name`;

        const nameSpan = createSpan(data.name, 'head');
        nameSpan.id = `roles_form-${rolesFormNum}-name_span`;

        const valueInput = document.createElement('input');
        valueInput.type = 'number';
        valueInput.name = `roles-${rolesFormNum}-value`;
        valueInput.id = `id_roles-${rolesFormNum}-value`;
        valueInput.value = data.value;
        valueInput.min = 0;

        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.id = `delete-role-${rolesFormNum}`;
        deleteButton.classList.add('btn', 'btn-danger', 'btn-sm');
        deleteButton.style.transform = 'scale(0.5, 0.5)';

        const deleteImage = document.createElement('i');
        deleteImage.classList.add('fas', 'fa-times');

        deleteButton.appendChild(deleteImage);

        deleteButton.addEventListener('click', (e) => {
            removeRole(e.currentTarget.id.match(/[0-9]+/g)[0]);
        });

        rolesContainer.append(nameInput, nameSpan, valueInput, deleteButton);

        rolesFormNum++;
        totalRoleForms.setAttribute('value', `${rolesFormNum}`);

        for (let i = 0; i < formNum; i++) {
            const charRole = usersContainer.querySelector(`#id_form-${i}-role`);
            const newOption = document.createElement('option');
            newOption.text = data.name;
            newOption.value = data.name;
            charRole.options.add(newOption);
        }

        roleSet.add(data.name);
    }
}

function removeRole(index, allowEmpty = false) {
    if ((allowEmpty || rolesFormNum > 1) && index >= 0 && index < rolesFormNum) {
        const roleSpan = rolesContainer.querySelector(`#roles_form-${index}-name_span`);

        for (let i = 0; i < formNum; i++) {
            const charRole = usersContainer.querySelector(`#id_form-${i}-role`);
            for (let j = 0; j < charRole.options.length; j++) {
                const option = charRole.options.item(j);
                if (option.text === roleSpan.textContent) {
                    charRole.options.remove(j);
                    break;
                }
            }
        }

        roleSet.delete(roleSpan.textContent);

        roleSpan.remove();
        rolesContainer.querySelector(`#id_roles-${index}-name`).remove();
        rolesContainer.querySelector(`#id_roles-${index}-value`).remove();
        rolesContainer.querySelector(`#delete-role-${index}`).remove();

        for (let i = +index + 1; i < rolesFormNum; i++) {
            const nameInput = rolesContainer.querySelector(`#id_roles-${i}-name`);
            nameInput.id = `id_roles-${i - 1}-name`;
            nameInput.name = `roles-${i - 1}-name`;

            const nameSpan = rolesContainer.querySelector(`#roles_form-${i}-name_span`);
            nameSpan.id = `roles_form-${i - 1}-name_span`;

            const valueInput = rolesContainer.querySelector(`#id_roles-${i}-value`);
            valueInput.name = `roles-${i - 1}-value`;
            valueInput.id = `id_roles-${i - 1}-value`;

            const deleteButton = rolesContainer.querySelector(`#delete-role-${i}`);
            deleteButton.id = `delete-role-${i - 1}`;
        }

        rolesFormNum--;
        totalRoleForms.setAttribute('value', `${rolesFormNum}`);
    }
}

searchBtn.addEventListener("click", e => {
    e.preventDefault()

    searchResults.replaceChildren();

    let excludeIds = [];
    let queryStr = '';

    Array.from(usersContainer.getElementsByClassName('character-pk-list')).forEach((el) => {
        excludeIds.push(el.getAttribute('value'));
    });

    if (excludeIds.length > 0) {
        queryStr = '?excludeIds=' + excludeIds.join('&excludeIds=');
    }

    const request = new Request((searchBar.value != '' ? `/pve/ratters/${searchBar.value}/` : '/pve/ratters/') + queryStr, { headers: { 'X-CSRFToken': csrftoken } });
    fetch(request,
        {
            method: "GET",
            credentials: "same-origin",
        }
    ).then(res => {
        res.json().then(data => {
            let results = [];
            data.result.forEach((value) => {
                const profile_image = document.createElement('img');
                profile_image.src = value.profile_pic;
                profile_image.classList.add('img-circle');
                profile_image.style.marginRight = "1rem";

                let characterInfo = createSpan(`${value.character_name} (${value.char_status})`);
                characterInfo.setAttribute('data-toggle', 'tooltip');
                characterInfo.setAttribute('data-placement', 'top');
                characterInfo.setAttribute('title', value.char_tooltip);

                let addButton = document.createElement('button');
                addButton.textContent = "Add";
                addButton.type = "button";
                addButton.classList.add('btn', 'btn-success');
                addButton.addEventListener('click', () => {
                    if (rolesFormNum > 0) {
                        addCharacter({ profilePic: value.user_pic, username: value.user_main_character_name, userId: value.user_id, characterPic: value.profile_pic, characterName: value.character_name, characterId: value.character_id });
                        searchResults.replaceChildren(createSpan('No results', 'all-cols head'));
                        searchBar.value = '';
                    } else {
                        alert('You have to add a role first!');
                    }
                })

                results.push(profile_image, characterInfo, addButton);
            })

            if (results.length > 0) {
                searchResults.replaceChildren(...results);
                $(function () {
                    $('[data-toggle="tooltip"]').tooltip()
                })
            } else {
                searchResults.replaceChildren(createSpan('No results', 'all-cols head'));
            }
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

submitRoleButton.addEventListener('click', (e) => {
    const form = document.getElementById('roleForm');
    const nameInput = form.querySelector('#id_roleName');
    const valueInput = form.querySelector('#id_roleValue');
    if (nameInput.value != '' && valueInput.value > 0) {
        addRole({ name: nameInput.value, value: valueInput.value });
        form.reset();
    }
});

document.querySelectorAll('button[id^="delete-row-"]').forEach((element) => {
    element.addEventListener('click', (el) => {
        removeCharacter(el.currentTarget.id.match(/[0-9]+/g)[0]);
    });
});

document.querySelectorAll('button[id^="delete-role-"]').forEach((element) => {
    element.addEventListener('click', (e) => {
        removeRole(e.currentTarget.id.match(/[0-9]+/g)[0]);
    });
    const eID = element.id.match(/[0-9]+/g)[0];
    const roleSpan = document.getElementById(`roles_form-${eID}-name_span`);
    roleSet.add(roleSpan.textContent);
});

customIncrementButton.addEventListener('click', (e) => {
    let value = customIncrementInput.value.replaceAll(',', "");
    incrementEstimatedTotal(value);
    customIncrementInput.setAttribute('value', 0);
});