# Comece aqui — projeto PUBLICO completamente separado

Este ZIP e um **NOVO projeto**, para um **NOVO repositorio**, sem historico Git, segredos, curriculo ou valores pessoais.
**Nao substitua nenhum arquivo do repositorio privado atual.** O repositorio privado anterior permanece como esta.

## Arquivos

- `.github/workflows/ci.yml`, `.github/workflows/run.yml`: testes e demonstracao manual (sem agendamento).
- `jobagent/`: CLI Python, busca em APIs publicas autorizadas, avaliacao explicavel e envio HMAC opcional.
- `apps_script/`: componente opcional de planilha Google independente (nao enviar e-mails).
- `config/*.example.json` e `data/`: exemplos inteiramente ficticios.
- `tests/`, `tools/`, `docs/`, `README.md`, `pyproject.toml`, `.gitignore`, `.env.example`.

## Primeiro passo sugerido: download e extracao

1. Baixe `OPEN_JOB_AGENT_REPOSITORIO_PUBLICO_v1.zip`.
2. Clique com o botao direito sobre o ZIP e selecione **Extrair Tudo**.
3. Confirme que foi criada a pasta `open-job-agent`, com `README.md`, `jobagent`, `config`, `tests` etc.
4. **Nao copie nem mescle** o conteudo com o projeto privado original.
5. Mande um print da pasta extraida (apenas nomes, sem arquivos de configuracao abertos).

O proximo passo, depois da confirmacao, sera criar um novo repositorio GitHub independente e fazer o primeiro commit exclusivamente com estes arquivos. Nao precisamos ativar segredo algum para a demonstracao.

## Como conferir (opcional)

Na pasta extraida, rode `py -m pip install -e ".[dev]"`, `py -m pytest -q` e `py -m jobagent.cli demo`. A saida esperada e resultado com **3 vagas ficticias** e `SYNC: skipped (local mode)`.

## Seguranca / limites

- Este pacote nao inclui `.git`; assim, commits antigos do projeto privado nao serao migrados.
- A demo nao acessa o Google, Gmail, Drive ou plataformas de vagas.
- Vagas reais ou planilhas privadas requerem configuracao proprietaria separada e novo segredo.
- Nenhuma funcionalidade de candidatura automatica foi implementada nesta versao publica.
- Testes locais nao comprovam deploy/integracao em contas de terceiros.
- Para desfazer: apague apenas a pasta `open-job-agent`; o repositorio privado nao e tocado.
