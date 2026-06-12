function getEmojiFlag(iso) {
    if (!iso) return "";
    // Trata códigos especiais do flagcdn (ex: gb-eng -> GB)
    if (iso.includes('-')) iso = iso.split('-')[0];
    const codePoints = iso.toUpperCase().split('').map(char => 127397 + char.charCodeAt(0));
    return String.fromCodePoint(...codePoints);
}

function abrirModalPalpites(jogoId) {
    const modalElement = document.getElementById('modalPalpites');
    const listaContainer = document.getElementById('lista-palpites-outros');
    const btnExportar = document.getElementById('btnExportarWhatsapp');

    if (!modalElement || !listaContainer) return;

    // Reset do botão de exportação
    if (btnExportar) btnExportar.style.display = 'none';

    // Loading com cor de destaque
    listaContainer.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-warning"></div></div>';
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
    modalInstance.show();

    fetch('/get_palpites_jogo/' + jogoId)
        .then(response => response.json())
        .then(data => {
            if (!data.palpites || data.palpites.length === 0) {
                // Corrigido: Usando text-white para melhor legibilidade no fundo verde escuro
                listaContainer.innerHTML = '<p class="text-center text-white opacity-75 p-3">Ninguém palpitou ainda. Seja o primeiro!</p>';
                return;
            }

            let html = '<table class="table-espios w-100"><tbody>';
            
            data.palpites.forEach(p => {
                html += `<tr><td class="fw-bold py-2 td-nome-espiao">${p.nome}</td>`;
                
                if (p.liberado) {
                    let badgeClass = 'bg-secondary';
                    if (p.pontos === 5) badgeClass = 'bg-success';
                    else if (p.pontos === 3) badgeClass = 'bg-info text-dark';
                    else if (p.pontos === 2) badgeClass = 'bg-warning text-dark';

                    html += `
                        <td class="text-center"><span class="placar-espiao">${p.result_a} x ${p.result_b}</span></td>
                        <td class="text-end"><span class="badge ${badgeClass}">${p.pontos} pts</span></td>`;
                // Dentro da função abrirModalPalpites, no else da visibilidade:
                } else {
                    // Usamos 'fas' para garantir que o ícone sólido carregue
                    html += `
                        <td colspan="2" class="text-end" style="color: rgba(255,255,255,0.4); padding-right: 15px !important;">
                            <i class="fas fa-eye-slash" title="Palpite Oculto" style="font-size: 1rem;"></i>
                        </td>`;
                }
                html += `</tr>`;
            });
            
            html += '</tbody></table>';
            
            if (!data.visibilidade_liberada) {
                html += `
                <div class="alert mt-3 mb-0 text-center" style="background-color: rgba(0,0,0,0.2); color: #fff; font-size: 0.75rem; border: 1px solid rgba(255,255,255,0.1);">
                    <i class="fas fa-info-circle me-2"></i>Placares revelados 10 min antes do jogo.
                </div>`;
            } else if (btnExportar) {
                // Se visibilidade liberada e botão existe (admin), mostra ele
                btnExportar.style.display = 'block';
                btnExportar.onclick = function() {
                    const flagA = getEmojiFlag(data.iso_a);
                    const flagB = getEmojiFlag(data.iso_b);

                    let mensagem = `⚽ *Bolão da Cabeça - Mesa de Palpites*\n\n`;
                    mensagem += `*${data.time_a}* ${flagA} x *${data.time_b}* ${flagB} \n`;
                    mensagem += `_(${data.data_hora})_\n\n`;

                    data.palpites.forEach(p => {
                        mensagem += `${p.nome}: ${p.result_a} x ${p.result_b}\n`;
                    });

                    mensagem += `--------------------------------------------\n`;
                    mensagem += `🔒 Os palpites deste jogo já estão fechados.`;

                    // Usando o mesmo endpoint e estilo de separador que funciona no ranking
                    const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(mensagem)}`;
                    window.open(url, '_blank');
                };
            }


            listaContainer.innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            listaContainer.innerHTML = '<p class="text-danger text-center p-3">Erro ao carregar dados.</p>';
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

document.addEventListener('DOMContentLoaded', function() {
    const celularInput = document.querySelector('input[name="phone"]');
    
    if (celularInput) {
        celularInput.addEventListener('input', function(e) {
            // Remove tudo o que não for dígito numérico
            let limpar = e.target.value.replace(/\D/g, '');
            
            // Divide o número em blocos para a formatação
            let mascara = limpar.match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            
            // Aplica os parênteses e o hífen
            e.target.value = !mascara[2] ? mascara[1] : '(' + mascara[1] + ') ' + mascara[2] + (mascara[3] ? '-' + mascara[3] : '');
        });
    }
});

