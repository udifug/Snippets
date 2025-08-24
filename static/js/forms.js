const code = document.getElementById('id_code');
const charCount = document.getElementById('charCount');

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