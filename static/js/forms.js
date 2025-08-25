const code = document.getElementById('id_code');
const name = document.getElementById('id_name');
const access = document.getElementById('id_access');
const lang = document.getElementById('id_lang');
const description = document.getElementById('id_description');
const tags = document.getElementById('id_tags');
const charCount = document.getElementById('charCount');

const formDataKey = 'draft';

code.addEventListener('input', () => {
    const count = code.value.length;
    let text = `${count}/5000`;
    charCount.innerHTML = text;

    charCount.classList.remove("low-limit", "medium-limit", "high-limit");

    if (count < 1500){
        charCount.classList.add("low-limit");
    }
    else if (count < 3000) {
        charCount.classList.add('medium-limit');
    }
    else {
        charCount.classList.add('high-limit')
    }
});

function saveDraft(){
    const formData = {
        name : name.value,
        access : access.value,
        code : code.value,
        lang : lang.value,
        description : description.value,
        tags : tags.value,
    };
    localStorage.setItem(formDataKey, JSON.stringify(formData));
    console.log('form save')
}

setInterval(saveDraft, 3000)


function loadDraft(){
    const data = localStorage.getItem(formDataKey);
    if (!data) return

    let restore = confirm("Restore data")
    if (!restore) return;
    const formData = JSON.parse(data);
    name.value = formData.name;
    access.value = formData.access;
    code.value = formData.code;
    lang.value = formData.lang;
    description.value = formData.description;
    tags.value = formData.tags;
}

document.addEventListener('DOMContentLoaded', loadDraft)

