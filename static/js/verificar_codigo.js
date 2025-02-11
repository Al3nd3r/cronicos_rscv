const inputs = document.querySelectorAll('.codigo');

inputs.forEach((input, index) => {
    input.addEventListener('input', (event) => {
        const inputValue = event.target.value.replace(/[^0-9]/g, '');
        event.target.value = inputValue;
        
        if (inputValue.length === 1) {
            const nextInput = inputs[index + 1];
            if (nextInput) {
                nextInput.focus();
            }
        }
    });

    input.addEventListener('keydown', (event) => {
        if (event.key === 'Backspace' && event.target.value.length === 0) {
            const previousInput = inputs[index - 1];
            if (previousInput) {
                previousInput.focus();
            }
        }
    });
});
