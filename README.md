# Consulta PMVG 1.0

## Descrição

O **Consulta PMVG 1.0** é uma aplicação desktop em Python/Tkinter que permite consultar, em tempo real, o Preço Máximo de Venda ao Governo (PMVG) definido pela CMED/ANVISA.

Principais recursos:

- **Download automático** da base de preços (formato XLS) diretamente do site da Anvisa, com barra de progresso.
- **Autocomplete** de medicamentos: digite ao menos 3 caracteres e escolha entre sugestões.
- Seleção de **marca** e **apresentação** do medicamento.
- Cálculo do preço **sem** e **com** ICMS, considerando alíquotas para cada unidade federativa.
- Interface gráfica intuitiva desenvolvida em **Tkinter**.

---

## Pré-requisitos

- Python 3.7 ou superior
- Acesso à internet durante o download da base

### Dependências Python

Liste as dependências no arquivo `requirements.txt`:

```
pandas>=2.0
openpyxl>=3.0
xlrd>=2.0
requests>=2.0
beautifulsoup4>=4.0
```

Instale com:

```bash
pip install -r requirements.txt
```

---

## Estrutura do Projeto

```
consulta-pmvg/
├── consulta_pmvg.py       # Script principal
├── requirements.txt       # Dependências
├── README.md              # Documentação deste projeto
└── ConsultaPMVGData/      # Pasta onde as bases XLS são armazenadas
```

---

## Uso

1. Execute o script:

   ```bash
   python consulta_pmvg.py
   ```

2. Na aplicação:
   - Clique em **Avançar** na tela inicial.
   - Selecione o **estado** desejado.
   - Digite no mínimo 3 caracteres do **medicamento**. Escolha na lista de sugestões.
   - Selecione a **marca** e a **apresentação**.
   - Confira o **preço sem** e **com ICMS**.

---

## Gerando Executável (Windows)

Para criar um executável standalone, utilize o **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed consulta_pmvg.py --icon=meu_icone.ico
```

- O `.exe` será gerado em `dist/consulta_pmvg.exe`.

---

## Criando Instalador (Setup)

Para distribuir via instalador, recomendamos o **Inno Setup**:

1. Instale o Inno Setup: https://jrsoftware.org/isinfo.php
2. Crie um script `setup_consulta_pmvg.iss` (exemplo na pasta `installer/`).
3. Compile no Inno Setup Compiler para gerar o instalador `.exe`.

---

## Licença

Este projeto está licenciado sob **CC BY-SA**. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Autor

Desenvolvido por **Thales Coelho**

---

## Contribuição

Contribuições são bem-vindas! Para sugerir melhorias ou reportar bugs:

1. Fork este repositório.
2. Crie uma branch: `git checkout -b minha-melhoria`.
3. Faça commit das mudanças: `git commit -m "Minha melhoria"`.
4. Push na branch: `git push origin minha-melhoria`.
5. Abra um Pull Request.

Obrigado por contribuir!

