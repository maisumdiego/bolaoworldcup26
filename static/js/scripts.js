// Espera o HTML carregar completamente antes de rodar os scripts
document.addEventListener("DOMContentLoaded", function() {

    // 1. O SCRIPT DA MÁSCARA DE TELEFONE
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function (e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    }

    // 2. O SCRIPT DE VALIDAÇÃO DO BOOTSTRAP
    const forms = document.querySelectorAll('.needs-validation')
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })

    // 3. O SCRIPT DO BALÃOZINHO DE AVISO DA SENHA (POPOVER)
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

    // 4. O SCRIPT DO BOTÃO DE MOSTRAR SENHA
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            // Verifica qual é o tipo atual da caixa de texto
            const isPassword = passwordInput.getAttribute('type') === 'password';
            
            // Se for password, muda pra text. Se não, muda pra password.
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            // Um charme extra: muda o emoji do botão
            this.textContent = isPassword ? '🙈' : '👁️';
        });
    }

});