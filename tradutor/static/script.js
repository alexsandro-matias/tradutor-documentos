const inputArquivo = document.getElementById("inputArquivo");
const areaConfirmacao = document.getElementById("areaConfirmacao");
const nomeArquivoSpan = document.getElementById("nomeArquivo");
const btnConfirmar = document.getElementById("btnConfirmar");
const btnExcluir = document.getElementById("btnExcluir");
const areaCarregando = document.getElementById("areaCarregando");
const areaResultado = document.getElementById("areaResultado");
const btnBaixar = document.getElementById("btnBaixar");
const mensagemErro = document.getElementById("mensagemErro");

let arquivoSelecionado = null;
let blobResultado = null;
let nomeArquivoSaida = "";

function resetarTela() {
    areaConfirmacao.classList.add("oculto");
    areaCarregando.classList.add("oculto");
    areaResultado.classList.add("oculto");
    mensagemErro.classList.add("oculto");
    btnConfirmar.classList.remove("oculto");
    btnConfirmar.disabled = true;
    inputArquivo.value = "";
    arquivoSelecionado = null;
    blobResultado = null;
    nomeArquivoSaida = "";
}

// Passo 1: quando o usuÃ¡rio seleciona um arquivo
inputArquivo.addEventListener("change", () => {
    if (inputArquivo.files.length > 0) {
        arquivoSelecionado = inputArquivo.files[0];
        nomeArquivoSpan.textContent = arquivoSelecionado.name;
        areaConfirmacao.classList.remove("oculto");
        areaResultado.classList.add("oculto");
        mensagemErro.classList.add("oculto");
        btnConfirmar.disabled = false;
    }
});

// Passo 2 (opÃ§Ã£o excluir): cancela o envio
btnExcluir.addEventListener("click", () => {
    resetarTela();
});

// Passo 2 (opÃ§Ã£o confirmar) + Passo 3 (loading) + Passo 4 (resultado)
btnConfirmar.addEventListener("click", async () => {
    if (!arquivoSelecionado) return;

    areaConfirmacao.classList.add("oculto");
    btnConfirmar.classList.add("oculto");
    areaCarregando.classList.remove("oculto");
    mensagemErro.classList.add("oculto");

    const formData = new FormData();
    formData.append("arquivo", arquivoSelecionado);

    try {
        const resposta = await fetch("/traduzir", {
            method: "POST",
            body: formData,
        });

        if (!resposta.ok) {
            // Erros do backend ainda vÃªm como JSON (HTTPException)
            const erro = await resposta.json();
            throw new Error(erro.detail || "Erro ao traduzir o arquivo.");
        }

        // Sucesso: a resposta agora Ã© o ARQUIVO BINÃ RIO traduzido (.txt ou .docx)
        blobResultado = await resposta.blob();

        // Extrai o nome do arquivo a partir do header Content-Disposition
        const disposition = resposta.headers.get("Content-Disposition") || "";
        const match = disposition.match(/filename="(.+)"/);
        nomeArquivoSaida = match ? match[1] : "traduzido_" + arquivoSelecionado.name;

        areaCarregando.classList.add("oculto");
        areaResultado.classList.remove("oculto");

    } catch (erro) {
        areaCarregando.classList.add("oculto");
        btnConfirmar.classList.remove("oculto");
        btnConfirmar.disabled = false;
        mensagemErro.textContent = erro.message;
        mensagemErro.classList.remove("oculto");
    }
});

// Passo 5: baixar o arquivo traduzido (usa o blob recebido do backend)
btnBaixar.addEventListener("click", () => {
    if (!blobResultado) return;

    const url = URL.createObjectURL(blobResultado);
    const link = document.createElement("a");
    link.href = url;
    link.download = nomeArquivoSaida;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    resetarTela();
});
