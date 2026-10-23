<div align="center">

# 🔎 Open Job Agent

### Um ponto de partida para criar seu próprio projeto de automação de vagas

**Python · APIs REST · GitHub Actions · Análise de compatibilidade · Google Sheets (opcional)**

[![Testes automatizados](https://github.com/Endrees7/open-job-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Endrees7/open-job-agent/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/Endrees7/open-job-agent/actions)
[![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-green)](LICENSE)

**Comece com três vagas fictícias, entenda o código e personalize o projeto no seu ritmo.**

[**🚀 Guia para começar**](docs/COMECE_AQUI.md) · [**⚙️ Configuração privada**](docs/CONFIGURACAO_PRIVADA.md) · [**🧩 Arquitetura**](docs/ARQUITETURA.md)

</div>

---

## 💡 Para quem é este projeto?

Para estudantes, profissionais em transição de carreira e desenvolvedores que desejam aprender a criar **seu próprio sistema de acompanhamento e análise de vagas**.

Você pode usá-lo de três maneiras:

1. **Explorar:** executar a demonstração pelo GitHub, sem instalar nada ou criar credenciais.
2. **Aprender:** baixar o código, executar testes e entender cada etapa.
3. **Personalizar:** criar seu próprio repositório, ajustar o perfil, configurar fontes permitidas e evoluir o sistema.

> **Importante:** esta é uma **base técnica reutilizável**, não um serviço de candidaturas pronto para produção. A demonstração usa dados fictícios. O sistema **não envia candidaturas**, não acessa Gmail nem contorna CAPTCHA, logins ou restrições de plataformas.

## ⚡ Comece aqui — dois caminhos

### Opção A: ver a demonstração pelo GitHub (sem instalar Python)

1. Abra a aba **[Actions](https://github.com/Endrees7/open-job-agent/actions)** deste repositório.
2. À esquerda, selecione **Open Job Agent (manual)** e abra **uma execução concluída**.
3. Clique no job **`run`** e procure o passo **Demo (safe with zero secrets)**.
4. Confira o resumo: **não são necessárias chaves, contas Google ou fontes reais** para visualizar os resultados públicos.

**Quer executar a demo você mesmo pelo GitHub?** Primeiro crie **sua cópia** com *Use this template* ou *Fork* (veja abaixo); depois abra **Actions** na sua cópia, habilite os workflows se o GitHub solicitar e escolha **Run workflow → `demo`**. Visitantes normalmente **não conseguem disparar workflows no repositório de outra pessoa**.

### Opção B: rodar no seu computador (Windows)

Requisitos: **Python 3.10 ou superior** e uma cópia do projeto. Veja o passo a passo com imagens de navegação descritas no [guia para iniciantes](docs/COMECE_AQUI.md).

Abra o **PowerShell dentro da pasta do projeto** e execute, uma linha por vez:

```powershell
py --version
py -m pip install -e ".[dev]"
py -m pytest -q
py -m jobagent.cli demo
```

Quando terminar, abra o arquivo **`build/report.json`**: ele contém os resultados da demonstração. A pasta `build/` é ignorada pelo Git.

**Resultado esperado para a amostra incluída:** três vagas fictícias processadas, zero erros e uma sinalizada para revisão. O relatório não prova a existência de vagas reais.

No Linux/macOS, substitua `py` por `python3` nos comandos, conforme sua instalação.

## 🧱 Faça deste projeto o seu ponto de partida

**Quer ter a sua própria versão?** Depois que este repositório estiver marcado como **Template repository**, clique em **Use this template → Create a new repository**. Escolha um nome e crie um repositório independente, com seus próprios arquivos e histórico inicial.

Se o botão ainda não aparecer, é possível usar **Fork** para criar sua cópia. Para entender a diferença e como continuar, siga [**Como criar e personalizar o seu Job Agent**](docs/COMECE_AQUI.md).

**Primeiras personalizações recomendadas:**

- Copie `config/profile.example.json` para **`config/private/profile.json`** e edite apenas a cópia privada.
- Copie `config/sources.example.json` para **`config/private/sources.json`** e adicione somente quadros de vagas públicos cujo acesso seja permitido.
- Ajuste as regras em `jobagent/scoring.py` **se quiser experimentar**, adicionando testes em `tests/`.
- Atualize o README da **sua cópia** para explicar o que você alterou e comprovou.

**Não publique seu currículo, e-mail, tokens, salário desejado ou arquivos da pasta `config/private/`.** Os exemplos fornecidos são fictícios.

## 🧠 Como funciona?

```text
          DEMONSTRAÇÃO                    BUSCA CONFIGURADA
       (JSON fictício local)       (APIs públicas de empregadores*)
                  \                         /
                   \                       /
                    v                     v
                      Coleta / normalização
                               |
                         Deduplicação
                               |
                   Compatibilidade (0 a 100)
                               |
                    Indicação para revisão
                               |
                    Relatório JSON privado
                               |
                     [Integração opcional]
                               v
                   Apps Script → Google Sheets
```

\* Os adaptadores Greenhouse, Lever e Ashby estão no código e foram testados com respostas simuladas. **Consultas a fontes reais e envio para Google Sheets não foram validados de ponta a ponta nesta versão pública.** Só configure fontes e integrações compatíveis com as regras dos respectivos serviços.

## ✅ O que já existe e o que ainda é experimental?

| Funcionalidade | Estado atual |
|---|---|
| Demonstração offline com 3 vagas fictícias | ✅ Executada com sucesso no GitHub Actions |
| Normalização, deduplicação e relatório JSON | ✅ Disponível e exercitado na demo |
| Pontuação heurística e justificativas para revisão | ✅ Implementadas e testadas |
| Testes automáticos | ✅ **27 testes aprovados** na execução inicial |
| GitHub Actions: CI e execução manual | ✅ Funcionando na demonstração |
| Adaptadores para Greenhouse, Lever e Ashby | 🧪 Testados com respostas simuladas; uso real ainda a validar |
| Google Apps Script e Google Sheets | 🔧 Integração opcional disponível no código; implantação real a validar |
| Candidaturas automáticas, geração de CV e Gmail | ⛔ Não implementados |

A pontuação **não representa probabilidade de contratação**. Informações ausentes, como remuneração ou elegibilidade, devem ser verificadas pela pessoa usuária.

## 🗂️ Onde alterar cada parte?

| Pasta/arquivo | Para que serve |
|---|---|
| `data/sample_jobs.json` | Três vagas fictícias da demonstração |
| `config/profile.example.json` | Modelo fictício de preferências de busca |
| `config/sources.example.json` | Modelo vazio de fontes de vagas |
| `config/private/` | Suas configurações reais **(não versionar)** |
| `jobagent/cli.py` | Comandos `demo`, `scan` e `test-webhook` |
| `jobagent/providers.py` | Leitura de APIs públicas compatíveis |
| `jobagent/scoring.py` | Regras de pontuação e revisão |
| `jobagent/pipeline.py` | Processamento, deduplicação e relatório |
| `jobagent/transport.py` | Comunicação assinada com endpoint opcional |
| `apps_script/` | Exemplo de integração com Google Sheets |
| `.github/workflows/` | Testes automáticos e execução manual |
| `tests/` | Verificação do funcionamento esperado |
| `docs/` | Instruções técnicas e de segurança |

## 🔐 Segurança desde o primeiro dia

- A **demo** não exige credenciais, faturamento, conta Google ou acesso a sites de vagas.
- Perfis reais, fontes privadas, credenciais, webhooks e relatórios **não devem entrar no Git**.
- `config/private/`, `.env` e `build/` já estão no `.gitignore`; **confira os arquivos antes de cada commit**.
- **`scan` é diferente de `demo`:** consulta fontes externas configuradas; só use depois de ler a [configuração privada](docs/CONFIGURACAO_PRIVADA.md).
- **Google Sheets é opcional e requer configuração separada**; não reutilize credenciais de outros projetos.
- O projeto não envia candidaturas automaticamente.

## 🆘 Travou em algum ponto?

No [guia para iniciantes](docs/COMECE_AQUI.md) você encontra o passo a passo completo: criar sua cópia, instalar Python, executar a demo, entender a saída, editar suas preferências, configurar fontes e resolver problemas comuns.

## 📚 Documentação

- [**COMECE AQUI — tutorial completo para iniciantes**](docs/COMECE_AQUI.md)
- [Configuração privada e integrações opcionais](docs/CONFIGURACAO_PRIVADA.md)
- [Arquitetura e decisões técnicas](docs/ARQUITETURA.md)
- [Segurança e publicação](docs/SEGURANCA_E_PUBLICACAO.md)

## 📄 Licença e créditos

Disponibilizado sob a [**Licença MIT**](LICENSE): você pode estudar, adaptar e compartilhar seu projeto, desde que preserve o aviso de direitos autorais e a licença. Este software é oferecido sem garantias.

Se usar como ponto de partida, um link de crédito para o projeto original é bem-vindo: **[Endrees7/open-job-agent](https://github.com/Endrees7/open-job-agent)**.

---

<div align="center">

**Comece pela demo → entenda os resultados → personalize com segurança → crie sua própria solução.**

</div>
