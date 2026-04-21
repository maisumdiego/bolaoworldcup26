function abrirModalPalpites(jogoId) {
    // Debug para você ver no console (F12) se o ID está chegando
    console.log("Iniciando busca para o Jogo ID:", jogoId);

    const modalElement = document.getElementById('modalPalpites');
    const listaContainer = document.getElementById('lista-palpites-outros');

    if (!modalElement || !listaContainer) {
        console.error("Elementos do modal não encontrados!");
        return;
    }

    // Limpa o conteúdo anterior e mostra carregamento
    listaContainer.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-warning"></div></div>';
    
    // Abre o modal
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
    modalInstance.show();

    // Chamada para a rota do Flask
    fetch('/get_palpites_jogo/' + jogoId)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'blocked') {
                listaContainer.innerHTML = `<div class="alert alert-dark text-center border-warning">${data.message}</div>`;
                return;
            }

            if (!data.palpites || data.palpites.length === 0) {
                listaContainer.innerHTML = '<p class="text-center text-muted">Nenhum palpite registrado.</p>';
                return;
            }

            let html = '<table class="table-espios w-100"><tbody>';
            data.palpites.forEach(p => {
                // Definimos uma cor para o badge de pontos
                let badgeClass = 'bg-secondary';
                if (p.pontos === 5) badgeClass = 'bg-success';
                else if (p.pontos === 3) badgeClass = 'bg-info text-dark';
                else if (p.pontos === 2) badgeClass = 'bg-warning text-dark';

                html += `
                <tr>
                    <td class="fw-bold">${p.nome}</td>
                    <td class="text-center"><span class="placar-espiao">${p.result_a} x ${p.result_b}</span></td>
                    <td class="text-end">
                        ${p.pontos !== undefined ? `<span class="badge ${badgeClass}">${p.pontos} pts</span>` : ''}
                    </td>
                </tr>`;
            });
            html += '</tbody></table>';
            listaContainer.innerHTML = html;
        });
}

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

