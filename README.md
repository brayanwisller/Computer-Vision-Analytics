# 👁️ Computer Vision Analytics

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> Ferramentas e scripts de análise em Visão Computacional focados no processamento e calibração de imagens utilizando Python e OpenCV.

## 📑 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 📖 Sobre o Projeto

O **Computer Vision Analytics** é um projeto desenvolvido em Python para tarefas de visão computacional. Ele contém scripts modulares para o processamento principal e para a calibração de cores/espaços (como HSV), facilitando a extração de dados e análise de imagens (ex: segmentação de grama ou detecção de objetos baseada em cor).

## 📂 Estrutura do Repositório

O projeto está organizado da seguinte forma:

```text
Computer-Vision-Analytics-main/
├── calibration.py          # Script focado em calibração de imagens e máscaras (ex: calibração HSV)
├── computer_vision_main.py # Script principal que executa a rotina de análise de visão computacional
├── grass_img.jpg           # Imagem de amostra/teste utilizada nos scripts
├── requirements.txt        # Dependências e bibliotecas do projeto (numpy, opencv-python, deepmerge)
└── .gitignore              # Arquivos e diretórios ignorados pelo Git (ex: venv, vscode, testes locais)
```

## ⚙️ Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado em sua máquina:
* [Python 3.8+](https://www.python.org/downloads/)
* Pip (Gerenciador de pacotes do Python)
* Git

## 🚀 Instalação

1. Clone o repositório para a sua máquina local:
```bash
git clone https://github.com/SEU_USUARIO/Computer-Vision-Analytics.git
cd Computer-Vision-Analytics
```

2. (Opcional, mas recomendado) Crie e ative um ambiente virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências necessárias através do arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

## 💻 Como Usar

O repositório possui duas frentes principais de execução.

### 1. Calibração (HSV / Filtros)
Para ajustar os parâmetros de visão computacional (como encontrar os valores corretos de cor em imagens), execute o script de calibração:
```bash
python calibration.py
```
*Dica: Utilize a imagem `grass_img.jpg` fornecida para testar os filtros e calibrações de verde/grama.*

### 2. Execução Principal
Para rodar a análise de visão computacional completa com os parâmetros já estabelecidos, execute:
```bash
python computer_vision_main.py
```

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Se você tem alguma ideia para melhorar este projeto, siga os passos abaixo:

1. Faça um Fork do projeto
2. Crie uma branch para a sua feature (`git checkout -b feature/MinhaFeatureIncrivel`)
3. Faça o commit das suas alterações (`git commit -m 'Add: Minha nova feature'`)
4. Faça o push para a branch (`git push origin feature/MinhaFeatureIncrivel`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---
Feito com ❤️ pela comunidade de Visão Computacional.