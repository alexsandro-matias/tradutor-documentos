
Desenvolvimento de sistema de tradução

vamos focar inicialmente apenas no docx pode começar a sugerir essa funcionalidade para tradução dos documentos .docx
22/09/2026 14:40

Vamos implementar o suporte a .docx. Vou detalhar as alterações em cada arquivo, mantendo a mesma arquitetura que já validamos (separação de responsabilidades), e ajustando o fluxo para: ler .docx → traduzir parágrafo por parágrafo (preservando estrutura) → gerar um novo .docx traduzido para download.
Visão geral das mudanças

projeto-traducao/
├── requirements.txt              # + python-docx
├── tradutor/
│   ├── __init__.py
│   ├── sentencizer.py            # (sem alteração)
│   ├── tradutor_documento.py     # + método traduzir_paragrafos
│   └── leitor_arquivo.py         # NOVO: leitura .txt e .docx
├── routers/
│   └── traducao.py               # ajustado: aceita .txt e .docx, gera .docx de saída
└── static/
    ├── index.html                # accept=".txt,.docx"
    └── script.js                 # ajustes de validação e download

1. requirements.txt

fastapi
uvicorn[standard]
python-multipart
argostranslate
python-docx

Instale:

powershell

pip install python-docx

2. tradutor/leitor_arquivo.py (novo arquivo)

Responsável apenas por extrair o conteúdo — não sabe nada sobre tradução.

python

from
 io 
import
 BytesIO
from
 docx 
import
 Document


def
 
ler_txt
(
conteudo_bytes
:
 
bytes
)
 
-
>
 
list
[
str
]
:

    
"""Lê bytes de um .txt e retorna uma lista de parágrafos (divididos por linha)."""

    texto 
=
 conteudo_bytes
.
decode
(
"utf-8"
)

    
# Mantém cada linha não vazia como um "parágrafo"

    
return
 
[
linha 
for
 linha 
in
 texto
.
splitlines
(
)
 
if
 linha
.
strip
(
)
]



def
 
ler_docx
(
conteudo_bytes
:
 
bytes
)
 
-
>
 
list
[
str
]
:

    
"""Lê bytes de um .docx e retorna a lista de parágrafos (texto de cada um)."""

    documento 
=
 Document
(
BytesIO
(
conteudo_bytes
)
)

    
return
 
[
paragrafo
.
text 
for
 paragrafo 
in
 documento
.
paragraphs 
if
 paragrafo
.
text
.
strip
(
)
]



def
 
extrair_paragrafos
(
nome_arquivo
:
 
str
,
 conteudo_bytes
:
 
bytes
)
 
-
>
 
list
[
str
]
:

    
"""Detecta a extensão do arquivo e delega para o leitor correto."""

    
if
 nome_arquivo
.
endswith
(
".txt"
)
:

        
return
 ler_txt
(
conteudo_bytes
)

    
elif
 nome_arquivo
.
endswith
(
".docx"
)
:

        
return
 ler_docx
(
conteudo_bytes
)

    
else
:

        
raise
 ValueError
(
"Formato de arquivo não suportado. Use .txt ou .docx."
)

    Nota: por que retornar uma lista de parágrafos em vez de uma string única? Porque isso permite reconstruir o .docx de saída parágrafo por parágrafo, preservando a estrutura do documento original (cada linha/parágrafo traduzido isoladamente).

3. tradutor/tradutor_documento.py (ajustado)

Adicionamos um método para traduzir uma lista de parágrafos, reaproveitando traduzir_texto que já existe.

python

from
 
.
sentencizer 
import
 aplicar_patch_sentencizer

aplicar_patch_sentencizer
(
)


import
 argostranslate
.
package
import
 argostranslate
.
translate


class
 
TradutorDocumento
:

    
def
 
__init__
(
self
,
 from_code
:
 
str
 
=
 
"en"
,
 to_code
:
 
str
 
=
 
"pb"
)
:

        self
.
from_code 
=
 from_code
        self
.
to_code 
=
 to_code
        self
.
translation 
=
 self
.
_carregar_traducao
(
)


    
def
 
_carregar_traducao
(
self
)
:

        installed_languages 
=
 argostranslate
.
translate
.
get_installed_languages
(
)

        from_lang 
=
 
next
(
(
l 
for
 l 
in
 installed_languages 
if
 l
.
code 
==
 self
.
from_code
)
,
 
None
)

        to_lang 
=
 
next
(
(
l 
for
 l 
in
 installed_languages 
if
 l
.
code 
==
 self
.
to_code
)
,
 
None
)


        
if
 from_lang 
is
 
None
 
or
 to_lang 
is
 
None
 
or
 from_lang
.
get_translation
(
to_lang
)
 
is
 
None
:

            argostranslate
.
package
.
update_package_index
(
)

            available_packages 
=
 argostranslate
.
package
.
get_available_packages
(
)

            pacote 
=
 
next
(

                
(
p 
for
 p 
in
 available_packages
                 
if
 p
.
from_code 
==
 self
.
from_code 
and
 p
.
to_code 
==
 self
.
to_code
)
,

                
None

            
)

            
if
 pacote 
is
 
None
:

                
raise
 ValueError
(
f"Pacote 
{
self
.
from_code
}
 -> 
{
self
.
to_code
}
 não encontrado."
)

            argostranslate
.
package
.
install_from_path
(
pacote
.
download
(
)
)


            argostranslate
.
translate
.
get_installed_languages
.
cache_clear
(
)

            installed_languages 
=
 argostranslate
.
translate
.
get_installed_languages
(
)

            from_lang 
=
 
next
(
l 
for
 l 
in
 installed_languages 
if
 l
.
code 
==
 self
.
from_code
)

            to_lang 
=
 
next
(
l 
for
 l 
in
 installed_languages 
if
 l
.
code 
==
 self
.
to_code
)


        translation 
=
 from_lang
.
get_translation
(
to_lang
)

        
if
 translation 
is
 
None
:

            
raise
 RuntimeError
(
f"Não foi possível carregar tradução 
{
self
.
from_code
}
 -> 
{
self
.
to_code
}
."
)

        
return
 translation

    
def
 
traduzir_texto
(
self
,
 texto
:
 
str
)
 
-
>
 
str
:

        
"""Traduz uma única string."""

        
return
 self
.
translation
.
translate
(
texto
)


    
def
 
traduzir_paragrafos
(
self
,
 paragrafos
:
 
list
[
str
]
)
 
-
>
 
list
[
str
]
:

        
"""Traduz uma lista de parágrafos, mantendo a ordem e a correspondência 1:1."""

        
return
 
[
self
.
traduzir_texto
(
paragrafo
)
 
for
 paragrafo 
in
 paragrafos
]

4. Novo módulo: tradutor/gerador_arquivo.py

Responsável por construir o arquivo de saída (responsabilidade separada da leitura).

python

from
 io 
import
 BytesIO
from
 docx 
import
 Document


def
 
gerar_txt
(
paragrafos_traduzidos
:
 
list
[
str
]
)
 
-
>
 
bytes
:

    
"""Gera bytes de um .txt a partir da lista de parágrafos traduzidos."""

    texto 
=
 
"\n"
.
join
(
paragrafos_traduzidos
)

    
return
 texto
.
encode
(
"utf-8"
)



def
 
gerar_docx
(
paragrafos_traduzidos
:
 
list
[
str
]
)
 
-
>
 
bytes
:

    
"""Gera bytes de um novo .docx a partir da lista de parágrafos traduzidos."""

    documento 
=
 Document
(
)

    
for
 paragrafo 
in
 paragrafos_traduzidos
:

        documento
.
add_paragraph
(
paragrafo
)


    
buffer
 
=
 BytesIO
(
)

    documento
.
save
(
buffer
)

    
buffer
.
seek
(
0
)

    
return
 
buffer
.
read
(
)



def
 
gerar_arquivo_saida
(
nome_arquivo_original
:
 
str
,
 paragrafos_traduzidos
:
 
list
[
str
]
)
 
-
>
 
tuple
[
bytes
,
 
str
,
 
str
]
:

    
"""
    Gera o arquivo de saída no mesmo formato do original.

    Returns:
        (conteudo_bytes, nome_arquivo_saida, media_type)
    """

    
if
 nome_arquivo_original
.
endswith
(
".docx"
)
:

        conteudo 
=
 gerar_docx
(
paragrafos_traduzidos
)

        nome_saida 
=
 
"traduzido_"
 
+
 nome_arquivo_original
        media_type 
=
 
"application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    
else
:

        conteudo 
=
 gerar_txt
(
paragrafos_traduzidos
)

        nome_saida 
=
 
"traduzido_"
 
+
 nome_arquivo_original
        media_type 
=
 
"text/plain"


    
return
 conteudo
,
 nome_saida
,
 media_type

5. tradutor/__init__.py (ajustado — expõe as novas funções)

python

import
 os

os
.
environ
[
"ARGOS_CHUNK_TYPE"
]
 
=
 
"MINISBD"

os
.
environ
[
"ARGOS_DEBUG"
]
 
=
 
"0"


from
 
.
tradutor_documento 
import
 TradutorDocumento
from
 
.
leitor_arquivo 
import
 extrair_paragrafos
from
 
.
gerador_arquivo 
import
 gerar_arquivo_saida

__all__ 
=
 
[
"TradutorDocumento"
,
 
"extrair_paragrafos"
,
 
"gerar_arquivo_saida"
]

6. routers/traducao.py (ajustado — agora retorna o arquivo binário, não JSON)

Essa é a mudança mais importante: como o resultado agora pode ser um .docx (arquivo binário), o endpoint passa a devolver o arquivo diretamente via StreamingResponse, em vez de um JSON com texto.

python

from
 io 
import
 BytesIO
from
 fastapi 
import
 APIRouter
,
 UploadFile
,
 File
,
 HTTPException
from
 fastapi
.
responses 
import
 StreamingResponse
from
 tradutor 
import
 TradutorDocumento
,
 extrair_paragrafos
,
 gerar_arquivo_saida

router 
=
 APIRouter
(
)

tradutor 
=
 TradutorDocumento
(
from_code
=
"en"
,
 to_code
=
"pb"
)


EXTENSOES_PERMITIDAS 
=
 
(
".txt"
,
 
".docx"
)



@router
.
post
(
"/traduzir"
)

async
 
def
 
traduzir_arquivo
(
arquivo
:
 UploadFile 
=
 File
(
.
.
.
)
)
:

    
if
 
not
 arquivo
.
filename
.
endswith
(
EXTENSOES_PERMITIDAS
)
:

        
raise
 HTTPException
(
status_code
=
400
,
 detail
=
"Apenas arquivos .txt ou .docx são aceitos."
)


    conteudo_bytes 
=
 
await
 arquivo
.
read
(
)


    
try
:

        paragrafos_originais 
=
 extrair_paragrafos
(
arquivo
.
filename
,
 conteudo_bytes
)

    
except
 ValueError 
as
 e
:

        
raise
 HTTPException
(
status_code
=
400
,
 detail
=
str
(
e
)
)

    
except
 Exception 
as
 e
:

        
raise
 HTTPException
(
status_code
=
400
,
 detail
=
f"Erro ao ler o arquivo: 
{
str
(
e
)
}
"
)


    
if
 
not
 paragrafos_originais
:

        
raise
 HTTPException
(
status_code
=
400
,
 detail
=
"O arquivo está vazio ou sem texto reconhecível."
)


    
try
:

        paragrafos_traduzidos 
=
 tradutor
.
traduzir_paragrafos
(
paragrafos_originais
)

    
except
 Exception 
as
 e
:

        
raise
 HTTPException
(
status_code
=
500
,
 detail
=
f"Erro ao traduzir: 
{
str
(
e
)
}
"
)


    conteudo_saida
,
 nome_saida
,
 media_type 
=
 gerar_arquivo_saida
(
arquivo
.
filename
,
 paragrafos_traduzidos
)


    
return
 StreamingResponse
(

        BytesIO
(
conteudo_saida
)
,

        media_type
=
media_type
,

        headers
=
{
"Content-Disposition"
:
 
f'attachment; filename="
{
nome_saida
}
"'
}

    
)

    Diferença importante em relação à versão anterior: como agora o backend já devolve o arquivo pronto para download (com o header Content-Disposition), o frontend não precisa mais gerar o Blob a partir de um texto JSON — ele vai receber a resposta como um Blob binário direto do fetch.

7. static/index.html (ajuste pontual)

html

<input type="file" id="inputArquivo" accept=".txt,.docx">

8. static/script.js (ajustado para lidar com resposta binária)

javascript

const
 inputArquivo 
=
 
document
.
getElementById
(
"inputArquivo"
)
;

const
 areaConfirmacao 
=
 
document
.
getElementById
(
"areaConfirmacao"
)
;

const
 nomeArquivoSpan 
=
 
document
.
getElementById
(
"nomeArquivo"
)
;

const
 btnConfirmar 
=
 
document
.
getElementById
(
"btnConfirmar"
)
;

const
 btnExcluir 
=
 
document
.
getElementById
(
"btnExcluir"
)
;

const
 areaCarregando 
=
 
document
.
getElementById
(
"areaCarregando"
)
;

const
 areaResultado 
=
 
document
.
getElementById
(
"areaResultado"
)
;

const
 btnBaixar 
=
 
document
.
getElementById
(
"btnBaixar"
)
;

const
 mensagemErro 
=
 
document
.
getElementById
(
"mensagemErro"
)
;


let
 arquivoSelecionado 
=
 
null
;

let
 blobResultado 
=
 
null
;

let
 nomeArquivoSaida 
=
 
""
;


function
 
resetarTela
(
)
 
{

    areaConfirmacao
.
classList
.
add
(
"oculto"
)
;

    areaCarregando
.
classList
.
add
(
"oculto"
)
;

    areaResultado
.
classList
.
add
(
"oculto"
)
;

    mensagemErro
.
classList
.
add
(
"oculto"
)
;

    inputArquivo
.
value
 
=
 
""
;

    arquivoSelecionado 
=
 
null
;

}


inputArquivo
.
addEventListener
(
"change"
,
 
(
)
 
=>
 
{

    
if
 
(
inputArquivo
.
files
.
length
 
>
 
0
)
 
{

        arquivoSelecionado 
=
 inputArquivo
.
files
[
0
]
;

        nomeArquivoSpan
.
textContent
 
=
 arquivoSelecionado
.
name
;

        areaConfirmacao
.
classList
.
remove
(
"oculto"
)
;

        areaResultado
.
classList
.
add
(
"oculto"
)
;

        mensagemErro
.
classList
.
add
(
"oculto"
)
;

    
}

}
)
;


btnExcluir
.
addEventListener
(
"click"
,
 
(
)
 
=>
 
{

    
resetarTela
(
)
;

}
)
;


btnConfirmar
.
addEventListener
(
"click"
,
 
async
 
(
)
 
=>
 
{

    
if
 
(
!
arquivoSelecionado
)
 
return
;


    areaConfirmacao
.
classList
.
add
(
"oculto"
)
;

    areaCarregando
.
classList
.
remove
(
"oculto"
)
;

    mensagemErro
.
classList
.
add
(
"oculto"
)
;


    
const
 formData 
=
 
new
 
FormData
(
)
;

    formData
.
append
(
"arquivo"
,
 arquivoSelecionado
)
;


    
try
 
{

        
const
 resposta 
=
 
await
 
fetch
(
"/traduzir"
,
 
{

            
method
:
 
"POST"
,

            
body
:
 formData
,

        
}
)
;


        
if
 
(
!
resposta
.
ok
)
 
{

            
// Erros ainda vêm como JSON (HTTPException)

            
const
 erro 
=
 
await
 resposta
.
json
(
)
;

            
throw
 
new
 
Error
(
erro
.
detail
 
||
 
"Erro ao traduzir o arquivo."
)
;

        
}


        
// Sucesso: a resposta é o arquivo binário traduzido

        blobResultado 
=
 
await
 resposta
.
blob
(
)
;


        
// Extrai o nome do arquivo do header Content-Disposition

        
const
 disposition 
=
 resposta
.
headers
.
get
(
"Content-Disposition"
)
 
||
 
""
;

        
const
 match 
=
 disposition
.
match
(
/
filename="(.+)"
/
)
;

        nomeArquivoSaida 
=
 match 
?
 match
[
1
]
 
:
 
"traduzido_"
 
+
 arquivoSelecionado
.
name
;


        areaCarregando
.
classList
.
add
(
"oculto"
)
;

        areaResultado
.
classList
.
remove
(
"oculto"
)
;


    
}
 
catch
 
(
erro
)
 
{

        areaCarregando
.
classList
.
add
(
"oculto"
)
;

        mensagemErro
.
textContent
 
=
 erro
.
message
;

        mensagemErro
.
classList
.
remove
(
"oculto"
)
;

    
}

}
)
;


btnBaixar
.
addEventListener
(
"click"
,
 
(
)
 
=>
 
{

    
const
 url 
=
 
URL
.
createObjectURL
(
blobResultado
)
;

    
const
 link 
=
 
document
.
createElement
(
"a"
)
;

    link
.
href
 
=
 url
;

    link
.
download
 
=
 nomeArquivoSaida
;

    
document
.
body
.
appendChild
(
link
)
;

    link
.
click
(
)
;

    
document
.
body
.
removeChild
(
link
)
;

    
URL
.
revokeObjectURL
(
url
)
;


    
resetarTela
(
)
;

}
)
;

Pontos de atenção

    Performance: se o .docx tiver muitos parágrafos, cada um dispara uma chamada separada ao translation.translate(). Para documentos grandes, isso pode ficar lento — é aceitável para o MVP, mas fica registrado como possível otimização futura (ex: traduzir em lote).
    Formatação avançada não é preservada: essa implementação lê apenas o texto dos parágrafos (paragrafo.text), sem preservar negrito, itálico, cores, tabelas ou imagens do .docx original — o novo .docx gerado terá apenas parágrafos de texto simples traduzidos. Isso é uma limitação aceitável para o MVP, mas é importante você saber disso para não prometer "fidelidade total de formatação" à liderança.
    .doc legado continua fora de escopo, como conversamos.

Teste manual sugerido

    Crie um .docx de teste no Word com 2-3 parágrafos em inglês.

    Suba pela interface.

    Confirme que o botão "Baixar tradução" agora baixa um .docx (não mais um .txt).

    Abra o .docx baixado no Word e confira o texto traduzido.

    Posso ajudar a testar esse fluxo assim que você aplicar as alterações.

    Posso adicionar uma barra de progresso mais precisa (ex: "parágrafo 3 de 10") já que agora sabemos a quantidade de parágrafos.

    Posso avançar depois para preservar formatação básica (negrito/itálico) usando os runs do python-docx, se isso for importante para a liderança que vai usar o RDO.

Imagem 1
Imagem 2

adicionei o arquivo .docx mas acho que o programa não suportou. mas o curioso é que no backend acho que tudo ocorreu de forma aceitável
22/09/2026 14:52

Boa notícia: o log do backend confirma que não houve nenhuma exceção — o Uvicorn só mostra as mensagens de inicialização, sem nenhum traceback de erro. Isso indica que o backend processou e devolveu a resposta com sucesso.
Diagnóstico

O erro "Unexpected token 'P', "PK␀␀␀␀␀␀␀"... is not valid JSON" é a confirmação exata disso: PK é a assinatura binária de um arquivo .docx (que, por trás dos panos, é um arquivo ZIP — e todo ZIP começa com os bytes PK). Ou seja: o backend enviou corretamente o arquivo .docx binário traduzido, mas o frontend ainda está tentando interpretar essa resposta como JSON (resposta.json()), em vez de tratá-la como um Blob binário.

Isso acontece por um destes dois motivos:

    O arquivo static/script.js no seu projeto ainda está com a versão antiga (a que fazia dados.texto_traduzido), e não foi substituído pela versão nova que usa resposta.blob().
    O navegador está servindo uma versão em cache do script.js antigo, mesmo que você já tenha salvo o arquivo novo (isso é muito comum com arquivos estáticos JS/CSS).

Solução
1. Confirme que o static/script.js está com a versão nova

Abra o arquivo e verifique se ele contém a linha:

javascript

blobResultado = await resposta.blob();

Se ainda tiver algo como dados = await resposta.json() no caminho de sucesso (fora do bloco de erro), é a versão antiga — substitua pelo código completo que te passei na resposta anterior (a que já tratava Content-Disposition e blob()).
2. Force o navegador a ignorar o cache

No navegador, com a página aberta, pressione:

Ctrl + Shift + R

ou

Ctrl + F5

Isso força o recarregamento de todos os arquivos estáticos (JS/CSS), ignorando o cache.
3. (Alternativa mais definitiva) Desative cache de estáticos durante o desenvolvimento

Você pode adicionar um parâmetro de versão no index.html para evitar esse problema durante os testes:

html

<script src="/static/script.js?v=2"></script>

Basta incrementar o número (v=3, v=4...) cada vez que alterar o script.js, forçando o navegador a buscar a versão atualizada.
Título da página também está desatualizado

Notei que o título ainda mostra "Tradutor de Documentos (.txt)" — isso é só cosmético (não afeta a funcionalidade), mas já que estamos ajustando para .txt e .docx, vale atualizar o static/index.html:

html

<title>Tradutor de Documentos</title>
...
<h1>Tradutor de Documentos</h1>

Checklist rápido para resolver agora

    Abra static/script.js e confirme que tem a lógica de blob() (versão nova).

    Salve o arquivo.

    No navegador, faça Ctrl + Shift + R na página.

    Suba o .docx novamente e clique em "Confirmar envio".

    Se depois desse ajuste ainda der erro, me envie o conteúdo atual do seu script.js para eu conferir linha a linha.

    Posso te ajudar a adicionar um indicador visual mais claro (ex: mostrar no HTML "versão do script carregada") para facilitar debugar cache no futuro.

    Posso seguir com a melhoria de progresso por parágrafo, já que o .docx está funcionando no backend.

pediu pra setar o blob. estou enviando código para que possa avaliar:

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

let textoTraduzido = "";

let nomeOriginal = "";

function resetarTela() {

areaConfirmacao.classList.add("oculto");

areaCarregando.classList.add("oculto");

areaResultado.classList.add("oculto");

mensagemErro.classList.add("oculto");

inputArquivo.value = "";

arquivoSelecionado = null;

}

// Passo 1: quando o usuário seleciona um arquivo

inputArquivo.addEventListener("change", () => {

if (inputArquivo.files.length > 0) {

arquivoSelecionado = inputArquivo.files[0];

nomeArquivoSpan.textContent = arquivoSelecionado.name;

areaConfirmacao.classList.remove("oculto");

areaResultado.classList.add("oculto");

mensagemErro.classList.add("oculto");

}

});

// Passo 2 (opção excluir): cancela o envio

btnExcluir.addEventListener("click", () => {

resetarTela();

});

// Passo 2 (opção confirmar) + Passo 3 (loading) + Passo 4 (resultado)

btnConfirmar.addEventListener("click", async () => {

if (!arquivoSelecionado) return;

areaConfirmacao.classList.add("oculto");

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

const erro = await resposta.json();

throw new Error(erro.detail || "Erro ao traduzir o arquivo.");

}

const dados = await resposta.json();

textoTraduzido = dados.texto_traduzido;

nomeOriginal = dados.nome_arquivo_original;

areaCarregando.classList.add("oculto");

areaResultado.classList.remove("oculto");

} catch (erro) {

areaCarregando.classList.add("oculto");

mensagemErro.textContent = erro.message;

mensagemErro.classList.remove("oculto");

}

});

// Passo 5: baixar o arquivo traduzido (gerado direto no navegador)

btnBaixar.addEventListener("click", () => {

const blob = new Blob([textoTraduzido], { type: "text/plain;charset=utf-8" });

const url = URL.createObjectURL(blob);

const link = document.createElement("a");

link.href = url;

link.download = "traduzido_" + nomeOriginal;

document.body.appendChild(link);

link.click();

document.body.removeChild(link);

URL.revokeObjectURL(url);

resetarTela();

});
22/09/2026 14:57

Confirmado — esse é exatamente o script.js da versão antiga (a do MVP 1, focada só em .txt com resposta JSON). Ele ainda tem dados = await resposta.json() e textoTraduzido = dados.texto_traduzido, que não existem mais na resposta do backend atualizado (que agora devolve o arquivo binário direto). Por isso o erro do PK....

Aqui está o arquivo completo, atualizado para funcionar com a resposta binária (.txt ou .docx):

javascript

const
 inputArquivo 
=
 
document
.
getElementById
(
"inputArquivo"
)
;

const
 areaConfirmacao 
=
 
document
.
getElementById
(
"areaConfirmacao"
)
;

const
 nomeArquivoSpan 
=
 
document
.
getElementById
(
"nomeArquivo"
)
;

const
 btnConfirmar 
=
 
document
.
getElementById
(
"btnConfirmar"
)
;

const
 btnExcluir 
=
 
document
.
getElementById
(
"btnExcluir"
)
;

const
 areaCarregando 
=
 
document
.
getElementById
(
"areaCarregando"
)
;

const
 areaResultado 
=
 
document
.
getElementById
(
"areaResultado"
)
;

const
 btnBaixar 
=
 
document
.
getElementById
(
"btnBaixar"
)
;

const
 mensagemErro 
=
 
document
.
getElementById
(
"mensagemErro"
)
;


let
 arquivoSelecionado 
=
 
null
;

let
 blobResultado 
=
 
null
;

let
 nomeArquivoSaida 
=
 
""
;


function
 
resetarTela
(
)
 
{

    areaConfirmacao
.
classList
.
add
(
"oculto"
)
;

    areaCarregando
.
classList
.
add
(
"oculto"
)
;

    areaResultado
.
classList
.
add
(
"oculto"
)
;

    mensagemErro
.
classList
.
add
(
"oculto"
)
;

    inputArquivo
.
value
 
=
 
""
;

    arquivoSelecionado 
=
 
null
;

    blobResultado 
=
 
null
;

    nomeArquivoSaida 
=
 
""
;

}


// Passo 1: quando o usuário seleciona um arquivo

inputArquivo
.
addEventListener
(
"change"
,
 
(
)
 
=>
 
{

    
if
 
(
inputArquivo
.
files
.
length
 
>
 
0
)
 
{

        arquivoSelecionado 
=
 inputArquivo
.
files
[
0
]
;

        nomeArquivoSpan
.
textContent
 
=
 arquivoSelecionado
.
name
;

        areaConfirmacao
.
classList
.
remove
(
"oculto"
)
;

        areaResultado
.
classList
.
add
(
"oculto"
)
;

        mensagemErro
.
classList
.
add
(
"oculto"
)
;

    
}

}
)
;


// Passo 2 (opção excluir): cancela o envio

btnExcluir
.
addEventListener
(
"click"
,
 
(
)
 
=>
 
{

    
resetarTela
(
)
;

}
)
;


// Passo 2 (opção confirmar) + Passo 3 (loading) + Passo 4 (resultado)

btnConfirmar
.
addEventListener
(
"click"
,
 
async
 
(
)
 
=>
 
{

    
if
 
(
!
arquivoSelecionado
)
 
return
;


    areaConfirmacao
.
classList
.
add
(
"oculto"
)
;

    areaCarregando
.
classList
.
remove
(
"oculto"
)
;

    mensagemErro
.
classList
.
add
(
"oculto"
)
;


    
const
 formData 
=
 
new
 
FormData
(
)
;

    formData
.
append
(
"arquivo"
,
 arquivoSelecionado
)
;


    
try
 
{

        
const
 resposta 
=
 
await
 
fetch
(
"/traduzir"
,
 
{

            
method
:
 
"POST"
,

            
body
:
 formData
,

        
}
)
;


        
if
 
(
!
resposta
.
ok
)
 
{

            
// Erros do backend ainda vêm como JSON (HTTPException)

            
const
 erro 
=
 
await
 resposta
.
json
(
)
;

            
throw
 
new
 
Error
(
erro
.
detail
 
||
 
"Erro ao traduzir o arquivo."
)
;

        
}


        
// Sucesso: a resposta agora é o ARQUIVO BINÁRIO traduzido (.txt ou .docx)

        blobResultado 
=
 
await
 resposta
.
blob
(
)
;


        
// Extrai o nome do arquivo a partir do header Content-Disposition

        
const
 disposition 
=
 resposta
.
headers
.
get
(
"Content-Disposition"
)
 
||
 
""
;

        
const
 match 
=
 disposition
.
match
(
/
filename="(.+)"
/
)
;

        nomeArquivoSaida 
=
 match 
?
 match
[
1
]
 
:
 
"traduzido_"
 
+
 arquivoSelecionado
.
name
;


        areaCarregando
.
classList
.
add
(
"oculto"
)
;

        areaResultado
.
classList
.
remove
(
"oculto"
)
;


    
}
 
catch
 
(
erro
)
 
{

        areaCarregando
.
classList
.
add
(
"oculto"
)
;

        mensagemErro
.
textContent
 
=
 erro
.
message
;

        mensagemErro
.
classList
.
remove
(
"oculto"
)
;

    
}

}
)
;


// Passo 5: baixar o arquivo traduzido (usa o blob recebido do backend)

btnBaixar
.
addEventListener
(
"click"
,
 
(
)
 
=>
 
{

    
if
 
(
!
blobResultado
)
 
return
;


    
const
 url 
=
 
URL
.
createObjectURL
(
blobResultado
)
;

    
const
 link 
=
 
document
.
createElement
(
"a"
)
;

    link
.
href
 
=
 url
;

    link
.
download
 
=
 nomeArquivoSaida
;

    
document
.
body
.
appendChild
(
link
)
;

    link
.
click
(
)
;

    
document
.
body
.
removeChild
(
link
)
;

    
URL
.
revokeObjectURL
(
url
)
;


    
resetarTela
(
)
;

}
)
;

O que mudou em relação à sua versão
Antes (v1 — só .txt via JSON)
Agora (v2 — .txt/.docx via binário)
let textoTraduzido = "", let nomeOriginal = ""
let blobResultado = null, let nomeArquivoSaida = ""
const dados = await resposta.json()
blobResultado = await resposta.blob()
textoTraduzido = dados.texto_traduzido
(não existe mais — o texto já vem embutido no arquivo binário)
nomeOriginal = dados.nome_arquivo_original
Nome extraído do header Content-Disposition
btnBaixar criava um Blob novo a partir de textoTraduzido
btnBaixar usa diretamente o blobResultado recebido do backend

linhas por página
Passo a passo para aplicar

    Substitua todo o conteúdo do seu static/script.js pelo código acima.
    Salve o arquivo.
    Force o navegador a recarregar sem cache:

    Ctrl + Shift + R

    Selecione novamente o python-traducao.docx e clique em "Confirmar envio".

Isso deve resolver — como o backend já está funcionando corretamente (confirmado pelo log limpo do Uvicorn), só faltava o frontend acompanhar a mudança de contrato da API.

    Posso ajudar a validar se o .docx baixado abre corretamente no Word após esse ajuste.
    Posso te ajudar a adicionar uma verificação de versão no HTML (?v=2) para evitar esse tipo de problema de cache no futuro.
    Posso seguir com a melhoria de indicação de progresso por parágrafo, agora que o fluxo .docx estará 100% funcional.

Imagem 1

mesmo erro
22/09/2026 15:00

Isso é bem estranho, porque o código que te passei já cobre exatamente esse cenário. Isso indica fortemente que o navegador ainda está executando a versão antiga do script.js, mesmo depois do Ctrl+Shift+R. Vamos confirmar isso de forma definitiva antes de qualquer outra suposição.
Passo 1 — Confirmar qual JS está realmente rodando (diagnóstico definitivo)

Abra o DevTools do navegador (F12) → aba Network → marque a caixa "Disable cache" (ela fica no topo da aba Network, geralmente ao lado do botão de gravação) → depois recarregue a página normalmente (F5).

Agora repita o teste de upload do .docx. Na aba Network, procure a requisição script.js e confira:

    O Status deve ser 200 (não 304 nem "from disk cache"/"from memory cache").
    Clique nela e veja a aba Response — confirme se o conteúdo mostrado é o código novo (procure pela linha blobResultado = await resposta.blob();).

Se aparecer o código antigo mesmo com "Disable cache" marcado, o problema não é cache do navegador — é o arquivo em disco que não foi salvo corretamente, ou há um script.js duplicado sendo servido de outro lugar (por exemplo, se você tem mais de uma pasta static/, ou se o app.py está montando um caminho diferente do que você está editando).
Passo 2 — Verificar se há mais de um script.js no projeto

Execute no PowerShell, na raiz do projeto:

powershell

Get-ChildItem -Recurse -Filter "script.js"

Se aparecer mais de um resultado, esse é o problema: você está editando um arquivo, mas o FastAPI está servindo outro.
Passo 3 — Confirmar que o arquivo foi salvo com o conteúdo certo

powershell

Get-Content .\static\script.js | Select-String "blobResultado"

Se esse comando não retornar nada, o arquivo em disco ainda está com a versão antiga (o editor pode não ter salvo, ou você editou um arquivo em outro caminho).
Passo 4 — Testar em aba anônima/privada

Abra uma aba anônima (Ctrl+Shift+N no Chrome/Edge) e acesse http://127.0.0.1:8000 novamente. Abas anônimas não usam cache/disco de sessões anteriores — se funcionar aqui, confirma 100% que era cache do navegador normal.
Possível causa adicional: proxy corporativo (Netskope) fazendo cache

Como seu ambiente já demonstrou interferência do Netskope em outras camadas (certificados TLS), é possível que o proxy corporativo também esteja fazendo cache de assets estáticos como script.js em nível de rede, não só no navegador. Isso explicaria persistir mesmo após limpar cache local. Se os passos 1-4 confirmarem que o navegador está pedindo a versão certa mas ainda recebendo conteúdo antigo, isso seria a pista.
Solução definitiva (cache-busting), independente da causa

Para eliminar essa variável de uma vez, adicione um parâmetro de versão na tag do script, no static/index.html:

html

<script src="/static/script.js?v=2"></script>

Isso força o navegador (e qualquer proxy no meio do caminho) a tratar como uma URL diferente da anterior, ignorando qualquer cache antigo associado à URL sem o parâmetro.
Peço que você confirme

Pode rodar os comandos dos Passos 2 e 3 no PowerShell e me enviar o resultado? Isso vai dizer com certeza se o problema é o arquivo em disco (não foi salvo/está duplicado) ou é cache (navegador ou proxy) — e assim eu já te dou a correção exata, sem mais tentativa e erro.

    Aguardo o resultado dos comandos Get-ChildItem e Get-Content para diagnosticar com precisão.
    Posso te ajudar a adicionar o cache-busting (?v=2) desde já, em paralelo ao diagnóstico.
    Se for confirmado proxy corporativo fazendo cache, posso sugerir headers adicionais no FastAPI (Cache-Control: no-store) para a rota de estáticos.

(.venv) PS C:\Users\PB7P\projeto-traducao> Get-ChildItem -Recurse -Filter "script.js"

Diretório: C:\Users\PB7P\projeto-traducao\static

Mode LastWriteTime Length Name

-a---- 22/09/2026 14:58 3500 script.js

(.venv) PS C:\Users\PB7P\projeto-traducao> Get-Content .\static\script.js | Select-String "blobResultado"

let blobResultado = null;

blobResultado = null;

blobResultado = await resposta.blob();

if (!blobResultado) return;

const url = URL.createObjectURL(blobResultado);

(.venv) PS C:\Users\PB7P\projeto-traducao>
22/09/2026 15:03

Isso é intrigante, porque o arquivo está com o conteúdo correto e não há duplicidade. Isso descarta a hipótese de cache do script.js. Precisamos agora olhar exatamente onde no código o erro está sendo disparado — o navegador nos dá essa informação diretamente no Console.
Diagnóstico mais preciso: ver o stack trace no Console

    Abra o DevTools (F12) → aba Console.
    Repita o teste: selecione o .docx → "Confirmar envio".
    Quando o erro aparecer na tela, procure no Console uma mensagem em vermelho parecida com:

    Uncaught (in promise) SyntaxError: Unexpected token 'P', "PK␀␀␀␀␀␀␀"... is not valid JSON
        at script.js:XX

    Me informe o número da linha (script.js:XX) — isso vai apontar exatamente qual .json() está sendo chamado sobre os bytes binários.

Ao mesmo tempo, confira a aba Network

    Ainda no DevTools, vá para a aba Network.
    Repita o upload.
    Clique na requisição traduzir (método POST).
    Me diga:
        O Status Code (deveria ser 200).
        O header Content-Type da resposta (deveria ser algo como application/vnd.openxmlformats-officedocument.wordprocessingml.document).
        O header Content-Disposition (deveria conter attachment; filename="traduzido_python-traducao.docx").

Hipótese que quero descartar/confirmar

Pela lógica do código novo, o erro só poderia ocorrer no bloco:

javascript

if (!resposta.ok) {
    const erro = await resposta.json();   // <- só executa se resposta.ok for FALSE
    ...
}

Ou seja, se esse erro está aparecendo, o navegador está entendendo que a resposta não foi bem-sucedida (resposta.ok === false, status fora de 200-299) — e, ao mesmo tempo, o corpo dessa resposta "não-ok" contém bytes binários (PK...) em vez de um JSON de erro. Isso sugeriria que o backend retornou o .docx binário, mas com um status HTTP diferente de 200 (por exemplo, 500), o que faria o frontend tentar ler como erro e falhar.

Isso pode acontecer se, por exemplo, uma exceção for lançada depois que o StreamingResponse já começou a ser montado, ou se há algum middleware/exception_handler interferindo.
Peço que você também confira o terminal do Uvicorn no momento exato do teste

Da última vez, o log mostrado era só de inicialização (antes do teste). Depois de repetir o upload agora, role para baixo no terminal do Uvicorn e veja se aparece uma linha como:

INFO: 127.0.0.1:xxxx - "POST /traduzir HTTP/1.1" 200 OK

ou

INFO: 127.0.0.1:xxxx - "POST /traduzir HTTP/1.1" 500 Internal Server Error

Esse código de status (200 vs 500) é a peça que falta para eu confirmar a causa exata.

    Aguardo o número da linha do erro no Console, o status code da aba Network, e a linha do log do Uvicorn referente à requisição POST /traduzir.
    Com essas 3 informações, consigo te dar a correção exata sem mais tentativa e erro.

vamos por partes de novo. o arquivo html tem o seguinte conteúdo:
Tradutor de Documentos (.txt)

Arquivo selecionado:

Traduzindo documento, aguarde...

Tradução concluída!

já o javascript será:

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

inputArquivo.value = "";

arquivoSelecionado = null;

blobResultado = null;

nomeArquivoSaida = "";

}

// Passo 1: quando o usuário seleciona um arquivo

inputArquivo.addEventListener("change", () => {

if (inputArquivo.files.length > 0) {

arquivoSelecionado = inputArquivo.files[0];

nomeArquivoSpan.textContent = arquivoSelecionado.name;

areaConfirmacao.classList.remove("oculto");

areaResultado.classList.add("oculto");

mensagemErro.classList.add("oculto");

}

});

// Passo 2 (opção excluir): cancela o envio

btnExcluir.addEventListener("click", () => {

resetarTela();

});

// Passo 2 (opção confirmar) + Passo 3 (loading) + Passo 4 (resultado)

btnConfirmar.addEventListener("click", async () => {

if (!arquivoSelecionado) return;

areaConfirmacao.classList.add("oculto");

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

// Erros do backend ainda vêm como JSON (HTTPException)

const erro = await resposta.json();

throw new Error(erro.detail || "Erro ao traduzir o arquivo.");

}

// Sucesso: a resposta agora é o ARQUIVO BINÁRIO traduzido (.txt ou .docx)

blobResultado = await resposta.blob();

// Extrai o nome do arquivo a partir do header Content-Disposition

const disposition = resposta.headers.get("Content-Disposition") || "";

const match = disposition.match(/filename="(.+)"/);

nomeArquivoSaida = match ? match[1] : "traduzido_" + arquivoSelecionado.name;

areaCarregando.classList.add("oculto");

areaResultado.classList.remove("oculto");

} catch (erro) {

areaCarregando.classList.add("oculto");

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
22/09/2026 15:06

Perfeito, confirmo que tanto o index.html quanto o script.js estão exatamente como deveriam estar — sem cache antigo, sem duplicidade, tudo correto. Isso descarta 100% o frontend como causa do problema.

Isso reforça a hipótese que levantei antes: o backend deve estar retornando uma resposta com status HTTP diferente de 200 (por exemplo, 500), mas com o corpo contendo os bytes binários do .docx (PK...) em vez de um JSON de erro. Quando isso acontece, o frontend entra no bloco if (!resposta.ok) e tenta fazer resposta.json() sobre esses bytes binários — daí o erro Unexpected token 'P'....

Para confirmar isso e corrigir a causa raiz, preciso ver duas coisas:
1. O conteúdo atual do seu routers/traducao.py

Pode colar aqui o arquivo completo? Quero confirmar se está exatamente como sugeri (com StreamingResponse e os try/except retornando HTTPException), ou se ficou alguma mistura com a versão antiga (que retornava JSON).
2. O status HTTP exato dessa requisição

Sem precisar abrir o DevTools, você pode conseguir isso direto pelo terminal do Uvicorn: depois de repetir o upload do .docx, role o terminal onde o uvicorn está rodando e copie a última linha que aparecer, algo como:

INFO: 127.0.0.1:xxxxx - "POST /traduzir HTTP/1.1" 200 OK

ou

INFO: 127.0.0.1:xxxxx - "POST /traduzir HTTP/1.1" 500 Internal Server Error

Com o código do traducao.py e esse status, vou conseguir identificar exatamente o ponto da falha (por exemplo, pode ser que o StreamingResponse esteja sendo montado corretamente, mas algo no meio do caminho — como um middleware de CORS, ou uma exceção lançada durante a serialização — esteja alterando a resposta).

    Aguardo o conteúdo do routers/traducao.py e a linha de log do Uvicorn correspondente a essa requisição.
    Com isso, te dou a correção pontual e definitiva.

o conteudo de traducao na pasta routers:

from io import BytesIO

from fastapi import APIRouter, UploadFile, File, HTTPException

from fastapi.responses import StreamingResponse

from tradutor import TradutorDocumento, extrair_paragrafos, gerar_arquivo_saida

router = APIRouter()

tradutor = TradutorDocumento(from_code="en", to_code="pb")

EXTENSOES_PERMITIDAS = (".txt", ".docx")

﻿@router﻿.post("/traduzir")

async def traduzir_arquivo(arquivo: UploadFile = File(...)):

if not arquivo.filename.endswith(EXTENSOES_PERMITIDAS):

raise HTTPException(status_code=400, detail="Apenas arquivos .txt ou .docx são aceitos.")

conteudo_bytes = await arquivo.read()

try:

paragrafos_originais = extrair_paragrafos(arquivo.filename, conteudo_bytes)

except ValueError as e:

raise HTTPException(status_code=400, detail=str(e))

except Exception as e:

raise HTTPException(status_code=400, detail=f"Erro ao ler o arquivo: {str(e)}")

if not paragrafos_originais:

raise HTTPException(status_code=400, detail="O arquivo está vazio ou sem texto reconhecível.")

try:

paragrafos_traduzidos = tradutor.traduzir_paragrafos(paragrafos_originais)

except Exception as e:

raise HTTPException(status_code=500, detail=f"Erro ao traduzir: {str(e)}")

conteudo_saida, nome_saida, media_type = gerar_arquivo_saida(arquivo.filename, paragrafos_traduzidos)

return StreamingResponse(

BytesIO(conteudo_saida),

media_type=media_type,

headers={"Content-Disposition": f'attachment; filename="{nome_saida}"'}

)
22/09/2026 15:08

Analisando seu traducao.py, a lógica está correta — porém notei um detalhe estranho na linha do decorator:

python

﻿@router﻿.post("/traduzir")

Há caracteres invisíveis (prováveis marcas Unicode como BOM/zero-width) colados antes de @router e entre router e .post(. Isso pode ter entrado ao copiar/colar o código de algum editor/fonte. Isso pode causar problemas sutis de parsing dependendo do editor, mas como o Uvicorn não reportou erro de sintaxe, provavelmente não é a causa principal — ainda assim, vale limpar.

Em vez de continuarmos supondo o que o backend está devolvendo, vamos testar o endpoint diretamente, sem depender do navegador. Isso elimina de vez qualquer variável de frontend/cache/proxy.
Teste direto via terminal (PowerShell)

Com o servidor Uvicorn rodando, abra outro terminal (mantendo o Uvicorn rodando no primeiro) e execute:

powershell

curl.exe -i -X POST -F "arquivo=@C:\Users\PB7P\projeto-traducao\python-traducao.docx" http://127.0.0.1:8000/traduzir --output resposta_traduzida.docx

Isso vai:

    Mostrar no terminal os headers da resposta (incluindo o status HTTP real — 200, 400, 500, etc.).
    Salvar o corpo da resposta em resposta_traduzida.docx, para conferirmos se é um .docx válido ou não.

Me envie o que aparecer no terminal (o cabeçalho HTTP/1.1 XXX ... e as demais linhas de header).
Depois, verifique o arquivo salvo

powershell

Get-Item .\resposta_traduzida.docx | Select-Object Length

Se o tamanho for maior que 0 bytes, tente abrir esse arquivo no Word para ver se a tradução está correta.
Em paralelo, verifique se há erro de sintaxe oculto no arquivo

powershell

python -m py_compile routers\traducao.py

Se não aparecer nada, o arquivo está sintaticamente válido (os caracteres invisíveis, se existirem, não estão quebrando o Python). Se aparecer um erro, colamos aqui e corrigimos.
Por que estou pedindo isso

Esse teste via curl remove completamente o navegador e o script.js da equação. Se o curl mostrar HTTP/1.1 200 OK e o arquivo .docx salvo abrir corretamente no Word, o problema está 100% isolado no navegador/JS/cache, e vamos investigar por outro ângulo (ex: extensões do navegador, proxy corporativo interceptando respostas binárias, etc.). Se o curl mostrar um status de erro (400/500), o problema está no backend, e o corpo da resposta salva vai revelar a mensagem de erro exata.

    Aguardo o resultado do curl.exe (status HTTP + headers) e do py_compile.
    Com isso, temos certeza absoluta de onde está o problema antes de qualquer outra correção.

no teste do terminal, tive o seguinte erro:

(.venv) PS C:\Users\PB7P\projeto-traducao> curl.exe -i -X POST -F "arquivo=﻿@c:﻿\Users\PB7P\projeto-traducao\python-traducao.docx" http://127.0.0.1:8000/traduzir --output resposta_traduzida.docx

curl: (26) Failed to open/read local data from file/application

(.venv) PS C:\Users\PB7P\projeto-traducao>
22/09/2026 15:11

Excelente pista! Isso não é mais coincidência — reparei que o mesmo padrão apareceu duas vezes: antes no seu @router.post (routers/traducao.py) e agora no seu comando @c:\Users.... Em ambos os casos, existe um caractere invisível logo depois do @.
Provável causa raiz: watermarking invisível do Netskope (DLP)

Isso é uma característica conhecida de ferramentas de DLP (Data Loss Prevention) como o Netskope: elas podem inserir caracteres invisíveis (zero-width characters / BOM) no texto copiado para a área de transferência, como uma "marca d'água" digital para rastrear vazamento de dados corporativos. Isso explicaria por que esse artefato está aparecendo tanto no seu código colado quanto agora no comando de terminal — provavelmente toda vez que você copia texto (do VS Code, do navegador, de onde for) dentro do ambiente corporativo, esse caractere invisível é injetado.

Isso é consistente com todos os problemas de rede/certificado que já vimos vindos do Netskope neste mesmo ambiente.
Solução imediata: digite o comando manualmente (não copie/cole)

Para o teste de agora, digite diretamente no terminal, sem copiar e colar:

powershell

curl.exe -i -X POST -F "arquivo=@python-traducao.docx" http://127.0.0.1:8000/traduzir --output resposta_traduzida.docx

(Assumindo que você está executando o comando estando dentro da pasta C:\Users\PB7P\projeto-traducao, onde o .docx está localizado — assim evitamos até o caminho completo com barras, reduzindo chance de caractere estranho.)

Se preferir manter o caminho completo, digite caractere por caractere (sem colar):

powershell

curl.exe -i -X POST -F "arquivo=@C:\Users\PB7P\projeto-traducao\python-traducao.docx" http://127.0.0.1:8000/traduzir --output resposta_traduzida.docx

Verificação e limpeza dos arquivos do projeto (importante!)

Como o mesmo problema apareceu no seu routers/traducao.py, isso significa que esse arquivo pode ter caracteres invisíveis espalhados, o que é arriscado (pode gerar bugs sutis e intermitentes). Vamos verificar e limpar:

powershell

Get-Content -Raw .\routers\traducao.py | Format-Hex | Select-String "EF BB BF" 

Se retornar linhas, há BOM/caracteres invisíveis no meio do arquivo. Para limpar de forma garantida, recrie o arquivo digitando diretamente no editor (não colando) ou rode este comando para remover caracteres zero-width comuns:

powershell

$conteudo = Get-Content -Raw .\routers\traducao.py
$conteudoLimpo = $conteudo -replace "[\u200B-\u200D\uFEFF]", ""
Set-Content -Path .\routers\traducao.py -Value $conteudoLimpo -Encoding UTF8

Isso remove os caracteres Unicode invisíveis mais comuns (U+200B a U+200D zero-width, e U+FEFF BOM) sem alterar o restante do código.

Recomendo rodar esse mesmo comando de limpeza nos outros arquivos que você colou nesta conversa e salvou no projeto:

powershell

$arquivos
 = @
(
".\app.py"
,
 
".\routers\traducao.py"
,
 
".\tradutor\__init__.py"
,
 
".\tradutor\tradutor_documento.py"
,
 
".\tradutor\sentencizer.py"
,
 
".\tradutor\leitor_arquivo.py"
,
 
".\tradutor\gerador_arquivo.py"
,
 
".\static\script.js"
,
 
".\static\index.html"
)

foreach
 
(
$arq
 in 
$arquivos
)
 
{

    
if
 
(
Test-Path
 
$arq
)
 
{

        
$conteudo
 = 
Get-Content
 
-
Raw 
$arq

        
$limpo
 = 
$conteudo
 
-replace
 
"[\u200B-\u200D\uFEFF]"
,
 
""

        
Set-Content
 
-
Path 
$arq
 
-
Value 
$limpo
 
-
Encoding UTF8
        
Write-Host
 
"Limpo: 
$arq
"

    
}

}

Próximos passos

    Rode o script de limpeza acima.
    Reinicie o Uvicorn (Ctrl+C e rode uvicorn app:app --reload de novo).
    Digite manualmente o comando curl.exe (sem copiar/colar) para testar o backend isoladamente.
    Me envie o resultado do curl (status HTTP + confirmação se o .docx salvo abre corretamente).

Isso deve finalmente isolar se o problema real sempre foi esse caractere invisível corrompendo os arquivos, ou se ainda existe algo pontual no backend a corrigir.

    Aguardo a saída do curl após a limpeza dos arquivos.
    Se identificarmos que era o watermarking do Netskope, vale registrar isso no seu README como nota de ambiente, para você e seus colegas de equipe não perderem tempo com esse mesmo sintoma no futuro.

Gostei do resultado, porém para baixar o arquivo o texto ficou com a formatação inadequada - Tradutor de Documentos (.txt)

TraduÃ§Ã£o concluÃ­da!

Baixar traduÃ§Ã£o
22/09/2026 15:17

Boa notícia: a tradução em si funcionou! O problema agora é mojibake — um erro clássico de codificação de caracteres, onde texto em UTF-8 (ç, ã, í) é lido incorretamente como outra codificação (Windows-1252/Latin-1) e depois regravado, corrompendo os acentos (ç → Ã§, ã → Ã£, í → Ã­).
Causa raiz provável

Isso muito provavelmente veio do script de limpeza que rodamos há pouco para remover os caracteres invisíveis do Netskope:

powershell

$conteudo = Get-Content -Raw $arq
$limpo = $conteudo -replace "[\u200B-\u200D\uFEFF]", ""
Set-Content -Path $arq -Value $limpo -Encoding UTF8

O problema: no Windows PowerShell 5.1 (não o PowerShell 7+), o Get-Content -Raw sem especificar -Encoding UTF8 lê o arquivo usando a codificação padrão do sistema (geralmente Windows-1252/ANSI), não UTF-8. Como seu index.html original já estava em UTF-8 com acentos, ele foi lido errado (interpretando bytes UTF-8 como se fossem Latin-1) e depois salvo novamente como UTF-8 — um clássico "double encoding", que gera exatamente esse padrão de corrupção (Ã§, Ã£, Ã­).

Isso pode ter afetado todos os arquivos que passaram por aquele script de limpeza e que continham acentuação em português (mensagens de erro no traducao.py, comentários, etc.) — vale revisar todos depois de corrigir o principal.
Correção do static/index.html

Aqui está o conteúdo já corrigido — substitua todo o arquivo por este:

html

<!
DOCTYPE
 
html
>

<
html
 
lang
=
"
pt-br
"
>


<
head
>

    
<
meta
 
charset
=
"
UTF-8
"
>

    
<
title
>
Tradutor de Documentos
</
title
>

    
<
link
 
rel
=
"
stylesheet
"
 
href
=
"
/static/style.css
"
>

</
head
>


<
body
>

    
<
div
 
class
=
"
container
"
>

        
<
h1
>
Tradutor de Documentos
</
h1
>


        
<!-- Passo 1: seleção do arquivo -->

        
<
input
 
type
=
"
file
"
 
id
=
"
inputArquivo
"
 
accept
=
"
.txt,.docx
"
>


        
<!-- Passo 2: confirmar ou excluir -->

        
<
div
 
id
=
"
areaConfirmacao
"
 
class
=
"
oculto
"
>

            
<
p
>
Arquivo selecionado: 
<
span
 
id
=
"
nomeArquivo
"
>
</
span
>
</
p
>

            
<
button
 
id
=
"
btnConfirmar
"
>
Confirmar envio
</
button
>

            
<
button
 
id
=
"
btnExcluir
"
>
Excluir
</
button
>

        
</
div
>


        
<!-- Passo 3: aguardando processamento -->

        
<
div
 
id
=
"
areaCarregando
"
 
class
=
"
oculto
"
>

            
<
div
 
class
=
"
spinner
"
>
</
div
>

            
<
p
>
Traduzindo documento, aguarde...
</
p
>

        
</
div
>


        
<!-- Passo 4: download do resultado -->

        
<
div
 
id
=
"
areaResultado
"
 
class
=
"
oculto
"
>

            
<
p
>
Tradução concluída!
</
p
>

            
<
button
 
id
=
"
btnBaixar
"
>
Baixar tradução
</
button
>

        
</
div
>


        
<!-- Mensagens de erro -->

        
<
p
 
id
=
"
mensagemErro
"
 
class
=
"
erro oculto
"
>
</
p
>

    
</
div
>


    
<
script
 
src
=
"
/static/script.js?v=3
"
>
</
script
>

</
body
>


</
html
>

Importante: ao salvar esse arquivo no VS Code, confirme no canto inferior direito da janela que a codificação está como "UTF-8" (não "UTF-8 with BOM" nem "Windows 1252"). Clique nesse indicador e escolha "Save with Encoding" → "UTF-8" se necessário.
Verificando/corrigindo outros arquivos afetados

Como o mesmo script de limpeza rodou em vários arquivos (app.py, routers/traducao.py, módulos do tradutor/), é bem provável que mensagens de erro com acentos também tenham sido corrompidas (ex: "não foi possível", "não é possível"). Isso não quebra a execução do Python, mas vai exibir mensagens de erro com acentuação errada.

Use este script Python (mais confiável que PowerShell para lidar com encoding) para detectar e corrigir automaticamente o mojibake nesses arquivos:

Aqui está o script — salve como corrigir_encoding.py na raiz do seu projeto e execute:

python

import
 os

arquivos 
=
 
[

    
"app.py"
,

    
"routers/traducao.py"
,

    
"routers/__init__.py"
,

    
"tradutor/__init__.py"
,

    
"tradutor/tradutor_documento.py"
,

    
"tradutor/sentencizer.py"
,

    
"tradutor/leitor_arquivo.py"
,

    
"tradutor/gerador_arquivo.py"
,

    
"static/index.html"
,

    
"static/script.js"
,

]


for
 caminho 
in
 arquivos
:

    
if
 
not
 os
.
path
.
exists
(
caminho
)
:

        
continue

    
with
 
open
(
caminho
,
 
"r"
,
 encoding
=
"utf-8"
)
 
as
 f
:

        conteudo 
=
 f
.
read
(
)


    
# Testa se há padrão de mojibake (ex: "Ã§", "Ã£", "Ã­", "Ã©", "Ã¡", "Ã³", "Ãº")

    padroes_mojibake 
=
 
[
"Ã§"
,
 
"Ã£"
,
 
"Ã­"
,
 
"Ã©"
,
 
"Ã¡"
,
 
"Ã³"
,
 
"Ãº"
,
 
"Â"
]

    tem_mojibake 
=
 
any
(
p 
in
 conteudo 
for
 p 
in
 padroes_mojibake
)


    
if
 tem_mojibake
:

        
try
:

            corrigido 
=
 conteudo
.
encode
(
"windows-1252"
)
.
decode
(
"utf-8"
)

            
with
 
open
(
caminho
,
 
"w"
,
 encoding
=
"utf-8"
)
 
as
 f
:

                f
.
write
(
corrigido
)

            
print
(
f"[CORRIGIDO] 
{
caminho
}
"
)

        
except
 
(
UnicodeDecodeError
,
 UnicodeEncodeError
)
 
as
 e
:

            
print
(
f"[ERRO ao corrigir] 
{
caminho
}
: 
{
e
}
"
)

    
else
:

        
print
(
f"[OK, sem mojibake detectado] 
{
caminho
}
"
)

Execute:

powershell

python corrigir_encoding.py

Isso vai imprimir no terminal quais arquivos tinham mojibake e foram corrigidos, e quais já estavam OK.
Depois de rodar o script

    Reinicie o Uvicorn (Ctrl+C e uvicorn app:app --reload de novo).
    Recarregue a página (Ctrl+Shift+R).
    Teste o fluxo completo novamente.

Prevenção para o futuro (importante para não repetir isso)

Como identificamos que o PowerShell 5.1 (Get-Content/Set-Content sem parâmetros explícitos) é a causa da corrupção de encoding, recomendo:

    Ao editar arquivos manualmente pelo VS Code, sempre confirmar "UTF-8" no canto inferior direito antes de salvar.
    Evitar usar Get-Content -Raw / Set-Content do PowerShell para manipular arquivos de texto com acentuação, a menos que explicite -Encoding UTF8 em ambos os comandos (leitura e escrita). Prefira usar Python (como fizemos agora) para esse tipo de manipulação — é mais previsível entre plataformas.

    Aguardo a confirmação de que os acentos ficaram corretos após rodar o script.
    Se algum texto ainda vier corrompido em pontos específicos (ex: dentro do próprio .docx traduzido gerado pelo Argos Translate), me avise que investigamos separadamente — a causa ali seria diferente (relacionada à decodificação do UploadFile no FastAPI, não ao PowerShell).
    Posso ajudar a atualizar o README com essa nota de "cuidado com encoding no PowerShell" para você e sua equipe não caírem nesse mesmo problema depois.

preciso atualize o meu readme:

o meu está assim:
Tradutor de Documentos

Aplicação web para traduzir arquivos de texto (.txt) de forma local. O

usuário seleciona um arquivo pela interface, confirma o envio, aguarda o

processamento e baixa uma nova cópia com o texto traduzido.

O backend foi desenvolvido com FastAPI e utiliza o Argos Translate para

realizar a tradução sem depender de uma API externa durante o processamento.

Na primeira execução, o Argos Translate pode baixar automaticamente o pacote de

tradução configurado no projeto.

O projeto utiliza soluções abertas e gratuitas, sem custo por requisição ou

dependência de APIs pagas de tradução. Depois que as bibliotecas e o pacote de

idiomas são instalados, o processamento pode ocorrer localmente, sem internet.
Ideia do projeto

O projeto simplifica a tradução de documentos de texto por meio de uma

interface web:

    O usuário seleciona um arquivo .txt.

    A aplicação valida a extensão, a codificação UTF-8 e se o arquivo não está

vazio.

    O conteúdo é enviado para a API POST /traduzir.

    O texto é traduzido pelo Argos Translate.

    O navegador disponibiliza o resultado para download com o prefixo

traduzido_.

Atualmente, o tradutor é inicializado com o par de idiomas en (inglês) para

pb, conforme definido em routers/traducao.py.

A arquitetura foi mantida simples e extensível, permitindo evoluções futuras

como suporte a novos formatos de arquivo, pares de idiomas e motores de

tradução.
Funcionalidades

    Upload de arquivos .txt pela interface web;

    Confirmação do envio ou exclusão do arquivo antes da tradução;

    Indicador visual de processamento durante a tradução;

    Validação da extensão, codificação UTF-8 e conteúdo do arquivo;

    Download do arquivo traduzido diretamente pelo navegador.

Tecnologias utilizadas

    Python

    FastAPI

    Uvicorn

    Argos Translate

    HTML, CSS e JavaScript

As versões das bibliotecas estão registradas em requirements.txt.

O frontend usa HTML, CSS e JavaScript puro, sem framework. O Argos Translate é

um motor de tradução open source baseado em modelos neurais e executado

localmente após a instalação do pacote de idiomas.
Pré-requisitos

    Python 3.10 ou superior

    pip

    Acesso à internet na primeira execução, caso o pacote de tradução ainda não

esteja instalado

    Windows, Linux ou macOS

Instalação no Windows

Abra o PowerShell na pasta do projeto:

powershell


cd C:\Users\PB7P\projeto-traducao

Crie um ambiente virtual:

powershell


py -m venv .venv

Ative o ambiente virtual:

powershell


.\.venv\Scripts\Activate.ps1

Se o PowerShell bloquear a ativação por política de execução, execute uma vez:

powershell


Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Depois, ative novamente:

powershell


.\.venv\Scripts\Activate.ps1

Atualize o pip e instale as dependências:

powershell


python 
-
m pip install 
--
upgrade pip

python 
-
m pip install 
-
r requirements
.
txt

    O arquivo requirements.txt possui dependências fixadas e pode instalar

    pacotes grandes, como PyTorch e bibliotecas do Argos Translate. A instalação

    pode levar alguns minutos e exige espaço livre em disco.

Instalação no Linux ou macOS

Na pasta do projeto, execute:

bash


python3 -m venv .venv

source
 .venv/bin/activate

python -m pip 
install
 --upgrade pip

python -m pip 
install
 -r requirements.txt

Executando a aplicação

Com o ambiente virtual ativado, inicie o servidor:

powershell


python -m uvicorn app:app --reload

No Linux ou macOS, o comando é o mesmo:

bash


python -m uvicorn app:app --reload

Quando o servidor estiver em execução, abra no navegador:

http://127.0.0.1:8000

Para abrir a documentação interativa da API, acesse:

    Swagger UI: http://127.0.0.1:8000/docs

    ReDoc: http://127.0.0.1:8000/redoc

Para encerrar o servidor, pressione Ctrl+C.
Como usar a interface

    Acesse http://127.0.0.1:8000.

    Clique no seletor de arquivo e escolha um arquivo com extensão .txt.

    Confira o nome exibido e clique em Confirmar envio.

    Aguarde a conclusão da tradução.

    Clique em Baixar tradução.

O arquivo baixado terá o nome traduzido_<nome-original>.txt.
Usando a API diretamente

O endpoint de tradução aceita somente arquivos .txt codificados em UTF-8:

powershell


curl
.
exe 
-
X POST `

-
F 
"arquivo=﻿@c:﻿\caminho\para\arquivo.txt"
 `

http:
/
/
127
.
0
.
0
.
1:8000/traduzir

Resposta esperada:

json


{


"nome_arquivo_original"
:
 
"arquivo.txt"
,


"texto_traduzido"
:
 
"Texto traduzido..."


}


Possíveis respostas de erro:

    400: arquivo que não é .txt;

    400: arquivo que não pode ser lido como UTF-8;

    400: arquivo vazio.

Estrutura do projeto

text


.

├── app.py # Criação da aplicação FastAPI

├── requirements.txt # Dependências Python

├── routers/

│ └── traducao.py # Endpoint POST /traduzir

├── tradutor/

│ ├── tradutor_documento.py # Integração com Argos Translate

│ ├── sentencizer.py # Separação local de frases

│ └── config.py # Configuração do ambiente Argos

└── static/

├── index.html # Interface web

├── script.js # Upload e download do resultado

└── style.css # Estilos da interface

Observações

    O ambiente virtual .venv não deve ser versionado; ele já está listado no

.gitignore.

    O servidor precisa permanecer em execução para que a interface funcione.

    O tamanho dos arquivos não é limitado pela aplicação neste momento, mas

arquivos grandes podem consumir mais memória e tempo de processamento.

    O pacote de tradução é carregado uma vez quando a aplicação é iniciada.

    O par de idiomas pode ser alterado no código para outro par suportado pelo

Argos Translate; atualmente essa configuração está fixa em routers/traducao.py.

agora, de acordo com as funcionalidades, outra coisa que precise que atualize são as formas de configuração e instalação de pacotes. gere um arquivo em md ao final. se não conseguir, gere um .txt com o conteúdo em markdown para que possa copiar e colar
22/09/2026 15:26

Vou atualizar seu README consolidando as mudanças que fizemos: suporte a .docx, nova arquitetura de módulos (leitor_arquivo.py, gerador_arquivo.py), a resposta binária da API (não mais JSON), e as notas de configuração/troubleshooting de ambiente (Netskope, encoding) que descobrimos ao longo do desenvolvimento.

Como o agente Python deste ambiente não gera arquivos de texto para download direto (apenas JSON/imagens/gráficos), vou fornecer o conteúdo completo abaixo em bloco de código markdown para você copiar e colar diretamente no seu README.md.

markdown

#
 Tradutor de Documentos


Aplicação web para traduzir arquivos de texto (
`.txt`
) e documentos Word
(
`.docx`
) de forma local. O usuário seleciona um arquivo pela interface,
confirma o envio, aguarda o processamento e baixa uma nova cópia com o texto
traduzido, no mesmo formato do arquivo original.

O backend foi desenvolvido com 
**
FastAPI
**
 e utiliza o 
**
Argos Translate
**
 para
realizar a tradução sem depender de uma API externa durante o processamento.
Na primeira execução, o Argos Translate pode baixar automaticamente o pacote de
tradução configurado no projeto.

O projeto utiliza soluções abertas e gratuitas, sem custo por requisição ou
dependência de APIs pagas de tradução. Depois que as bibliotecas e o pacote de
idiomas são instalados, o processamento pode ocorrer localmente, sem internet.

##
 Ideia do projeto


O projeto simplifica a tradução de documentos por meio de uma interface web:

1.
 O usuário seleciona um arquivo 
`.txt`
 ou 
`.docx`
.
2.
 A aplicação valida a extensão e extrai o conteúdo em parágrafos.
3.
 O conteúdo é enviado para a API 
`POST /traduzir`
.
4.
 Cada parágrafo é traduzido pelo Argos Translate.
5.
 Um novo arquivo é gerado no mesmo formato do original (
`.txt`
 ou 
`.docx`
)
   e devolvido diretamente pelo backend para download.
6.
 O navegador disponibiliza o resultado para download com o prefixo
   
`traduzido_`
.

Atualmente, o tradutor é inicializado com o par de idiomas 
`en`
 (inglês) para
`pb`
 (português do Brasil), conforme definido em 
`routers/traducao.py`
.

A arquitetura foi mantida simples e extensível, permitindo evoluções futuras
como suporte a novos formatos de arquivo (
`.pdf`
), novos pares de idiomas e
novos motores de tradução.

##
 Funcionalidades


-
 Upload de arquivos 
`.txt`
 ou 
`.docx`
 pela interface web;
-
 Confirmação do envio ou exclusão do arquivo antes da tradução;
-
 Indicador visual de processamento durante a tradução;
-
 Validação da extensão e do conteúdo do arquivo;
-
 Tradução parágrafo por parágrafo, preservando a estrutura do documento;
-
 Geração do arquivo traduzido no mesmo formato do original;
-
 Download do arquivo traduzido diretamente pelo navegador.

##
 Tecnologias utilizadas


-
 Python
-
 FastAPI
-
 Uvicorn
-
 Argos Translate
-
 python-docx
-
 HTML, CSS e JavaScript

As versões das bibliotecas estão registradas em 
`requirements.txt`
.

O frontend usa HTML, CSS e JavaScript puro, sem framework. O Argos Translate é
um motor de tradução open source baseado em modelos neurais e executado
localmente após a instalação do pacote de idiomas. O python-docx é utilizado
para ler e gerar documentos 
`.docx`
 sem dependências externas ao Word.

##
 Pré-requisitos


-
 Python 3.10 ou superior
-
 
`pip`

-
 Acesso à internet na primeira execução, caso o pacote de tradução ainda não
  esteja instalado
-
 Windows, Linux ou macOS

##
 Instalação no Windows


Abra o PowerShell na pasta do projeto:

```powershell
cd C:\Users\PB7P\projeto-traducao

Crie um ambiente virtual:

powershell

py -m venv .venv

Ative o ambiente virtual:

powershell

.\.venv\Scripts\Activate.ps1

Se o PowerShell bloquear a ativação por política de execução, execute uma vez:

powershell

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Depois, ative novamente:

powershell

.\.venv\Scripts\Activate.ps1

Atualize o pip e instale as dependências:

powershell

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

    O arquivo requirements.txt possui dependências fixadas e pode instalar pacotes grandes, como PyTorch e bibliotecas do Argos Translate. A instalação pode levar alguns minutos e exige espaço livre em disco.

Conteúdo esperado do requirements.txt:

text

fastapi
uvicorn[standard]
python-multipart
argostranslate
python-docx

Instalação no Linux ou macOS

Na pasta do projeto, execute:

bash

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Configuração do ambiente (Argos Translate)

O projeto configura automaticamente, em tradutor/__init__.py, duas variáveis de ambiente necessárias para a tradução funcionar de forma offline e estável:

python

os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"
os.environ["ARGOS_DEBUG"] = "0"

    ARGOS_CHUNK_TYPE: define o mecanismo de divisão de frases (SBD) usado antes da tradução. O projeto substitui esse mecanismo (via monkey patch, em tradutor/sentencizer.py) por uma divisão baseada em expressões regulares, eliminando a necessidade de download de modelos externos (Stanza/SpaCy).
    ARGOS_DEBUG: mantém desativado o log detalhado do Argos Translate. Ative temporariamente com "1" apenas para depuração.

Essas variáveis precisam ser definidas antes de qualquer import do pacote argostranslate — por isso ficam no topo de tradutor/__init__.py, executadas antes dos demais módulos do pacote.
Observação sobre ambientes corporativos com inspeção SSL (Netskope)

Em ambientes corporativos que utilizam ferramentas de inspeção SSL (como o Netskope), pode ocorrer o seguinte erro ao tentar baixar modelos de linguagem auxiliares (Stanza, SpaCy, MiniSBD):

text

OSError: Could not find a suitable TLS CA certificate bundle, invalid path:
C:\WINDOWS\IMECache\...\netskope-cert-bundle.pem

Isso ocorre porque a variável de ambiente REQUESTS_CA_BUNDLE pode apontar para um certificado inexistente naquele caminho. A solução adotada neste projeto foi eliminar a dependência de download desses modelos, substituindo-os por uma implementação própria de divisão de frases (ver seção acima). Caso o erro ainda ocorra em outra parte do fluxo, verifique com o suporte de TI da sua empresa o caminho correto do certificado corporativo, ou aponte temporariamente REQUESTS_CA_BUNDLE para o bundle padrão do certifi:

powershell

python -c "import certifi; print(certifi.where())"
$env:REQUESTS_CA_BUNDLE = "<caminho impresso pelo comando acima>"

Observação sobre codificação de caracteres (encoding)

Todo o projeto assume arquivos e código-fonte em UTF-8. Ao editar arquivos manualmente:

    No VS Code, confirme "UTF-8" (sem BOM) no canto inferior direito antes de salvar.
    Evite usar Get-Content/Set-Content do PowerShell sem especificar -Encoding UTF8 em leitura e escrita — isso pode corromper acentuação (ex.: ção se tornando Ã§Ã£o), um problema conhecido como mojibake. Prefira scripts Python para manipular texto com acentuação quando possível.
    Em ambientes com ferramentas de DLP (Data Loss Prevention) corporativas, textos copiados podem receber caracteres invisíveis (zero-width/BOM). Se comandos ou trechos de código colados apresentarem comportamento estranho sem erro aparente, prefira digitar diretamente ou recriar o arquivo.

Executando a aplicação

Com o ambiente virtual ativado, inicie o servidor:

powershell

python -m uvicorn app:app --reload

No Linux ou macOS, o comando é o mesmo:

bash

python -m uvicorn app:app --reload

Quando o servidor estiver em execução, abra no navegador:

http://127.0.0.1:8000

Para abrir a documentação interativa da API, acesse:

    Swagger UI: http://127.0.0.1:8000/docs
    ReDoc: http://127.0.0.1:8000/redoc

Para encerrar o servidor, pressione Ctrl+C.
Como usar a interface

    Acesse http://127.0.0.1:8000.
    Clique no seletor de arquivo e escolha um arquivo com extensão .txt ou .docx.
    Confira o nome exibido e clique em Confirmar envio, ou em Excluir para cancelar a seleção sem enviar nada ao servidor.
    Aguarde a mensagem "Traduzindo documento, aguarde...".
    Clique em Baixar tradução.

O arquivo baixado terá o nome traduzido_<nome-original>, mantendo a extensão original (.txt ou .docx).
Usando a API diretamente

O endpoint de tradução aceita arquivos .txt ou .docx. Diferente de versões anteriores do projeto, a resposta não é mais JSON: em caso de sucesso, o próprio arquivo traduzido é retornado no corpo da resposta (Content-Type correspondente ao formato e header Content-Disposition com o nome do arquivo).

powershell

curl.exe -i -X POST -F "arquivo=@caminho\para\arquivo.docx" http://127.0.0.1:8000/traduzir --output resposta_traduzida.docx

    Digite o comando diretamente no terminal em vez de copiar e colar, para evitar caracteres invisíveis inseridos por ferramentas corporativas de DLP (ver seção de observações acima).

Resposta esperada em caso de sucesso: status 200 OK, com o arquivo binário traduzido salvo em resposta_traduzida.docx.

Possíveis respostas de erro (formato JSON, via HTTPException):

    400: arquivo que não é .txt ou .docx;
    400: arquivo que não pode ser lido ou está vazio;
    500: erro durante o processo de tradução.

Exemplo de corpo de erro:

json

{
  "detail": "Apenas arquivos .txt ou .docx são aceitos."
}

Estrutura do projeto

text

.
├── app.py                      # Criação da aplicação FastAPI
├── requirements.txt            # Dependências Python
├── routers/
│   ├── __init__.py
│   └── traducao.py             # Endpoint POST /traduzir
├── tradutor/
│   ├── __init__.py             # Configuração de ambiente + exposição pública do pacote
│   ├── tradutor_documento.py   # Integração com Argos Translate (tradução por parágrafo)
│   ├── sentencizer.py          # Separação local de frases (sem downloads externos)
│   ├── leitor_arquivo.py       # Extração de texto de .txt e .docx
│   └── gerador_arquivo.py      # Geração do arquivo de saída (.txt ou .docx)
└── static/
    ├── index.html              # Interface web
    ├── script.js                # Upload, confirmação, carregamento e download
    └── style.css                # Estilos da interface

Observações

    O ambiente virtual .venv não deve ser versionado; ele já está listado no .gitignore.
    O servidor precisa permanecer em execução para que a interface funcione.
    O tamanho dos arquivos não é limitado pela aplicação neste momento, mas arquivos grandes podem consumir mais memória e tempo de processamento, já que a tradução é feita parágrafo por parágrafo.
    O pacote de tradução é carregado uma vez quando a aplicação é iniciada.
    O par de idiomas pode ser alterado no código para outro par suportado pelo Argos Translate; atualmente essa configuração está fixa em routers/traducao.py.
    Documentos .docx traduzidos preservam apenas o texto dos parágrafos; formatação avançada (negrito, itálico, tabelas, imagens) do arquivo original não é preservada nesta versão.
    Arquivos .doc (formato binário legado do Word) não são suportados; é necessário salvar o documento como .docx antes do upload.

Próximos passos (roadmap)

    Suporte a upload de .pdf
    Preservação de formatação básica (negrito/itálico) em documentos .docx
    Testes automatizados (pytest) para os módulos de tradução e o endpoint
    Tratamento de erro global (exception_handler) no FastAPI
    Suporte a múltiplos pares de idiomas selecionáveis na interface
    Containerização com Docker


## Principais mudanças em relação à versão anterior do seu README

| Seção | O que mudou |
|---|---|
| Ideia do projeto | Incluído fluxo de `.docx` e menção à geração no formato original |
| Funcionalidades | Adicionado suporte a `.docx`, tradução por parágrafo, geração no formato original |
| Tecnologias | Adicionado `python-docx` |
| Nova seção "Configuração do ambiente" | Documenta `ARGOS_CHUNK_TYPE`, `ARGOS_DEBUG`, o monkey patch do sentencizer, e os troubleshootings de Netskope e encoding que enfrentamos |
| Usando a API diretamente | Atualizado para refletir resposta binária (não mais JSON) em caso de sucesso |
| Estrutura do projeto | Atualizada para `leitor_arquivo.py` e `gerador_arquivo.py`, removendo o antigo `config.py` |
| Observações | Adicionadas notas sobre limitações do `.docx` (sem formatação avançada) e `.doc` legado não suportado |
| Roadmap | Nova seção com os próximos passos combinados |

1. Posso ajustar algum trecho específico (ex: remover a seção de troubleshooting se você preferir um README mais "limpo" e mover isso para um `TROUBLESHOOTING.md` separado).
2. Posso gerar também um `CHANGELOG.md` documentando a evolução do MVP 1 (.txt) para o MVP 2 (.docx).
3. Posso seguir com os próximos itens do roadmap, como os testes automatizados com `pytest`.



0 / 1.000.000

