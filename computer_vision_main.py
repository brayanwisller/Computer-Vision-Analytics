import cv2
import numpy as np
import json
import time
import os
from pathlib import Path
import argparse

def status_porcentagem(porcentagem: float) -> tuple:
    if porcentagem >= 80:
        cor_status = (0, 255, 0)
    elif porcentagem < 80 and porcentagem >= 50:
        cor_status = (255, 255, 0)
    else:
        cor_status = (0, 0, 255)

    return cor_status

def criar_gauge_dinamica(imagem_jpg: np.ndarray, porcentagem: float, x=20, y=20, largura=230, altura=55):
    porcentagem = max(0.0, min(100.0, porcentagem))

    cv2.rectangle(imagem_jpg, (x, y), (x + largura, y + altura), (25, 25, 25), -1)
    cv2.rectangle(imagem_jpg, (x, y), (x + largura, y + altura), (80, 80, 80), 1)

    bar_x = x + 12
    bar_y = y + 28
    bar_w = largura - 24
    bar_h = 14

    for i in range(bar_w):
        ratio = i / float(bar_w)

        if ratio < 0.5:
            fator = ratio / 0.5
            b, g, r = 0, int(255 * fator), 255
        else:
            fator = (ratio - 0.5) / 0.5
            b, g, r = 0, 255, int(255 * (1.0 - fator))

        cv2.line(imagem_jpg, (bar_x + i, bar_y), (bar_x + i,  bar_y + bar_h), (b, g, r), 1)

    cv2.rectangle(imagem_jpg, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 1)

    ponteiro_x = bar_x + int((porcentagem / 100.0) * bar_w)

    ponteiros = np.array([
        [ponteiro_x, bar_y - 2],
        [ponteiro_x - 5, bar_y - 8],
        [ponteiro_x + 5, bar_y - 8]
    ], np.int32)

    cv2.drawContours(imagem_jpg, [ponteiros], 0, (255, 255, 255), -1)
    cv2.drawContours(imagem_jpg, [ponteiros], 0, (0, 0, 0), 1)

    cv2.line(imagem_jpg, (ponteiro_x, bar_y), (ponteiro_x, bar_y + bar_h), (255, 255, 255), 2)

    cor_status = status_porcentagem(porcentagem)
    texto = f"Qualidade: {porcentagem:.2f}%"
    cv2.putText(imagem_jpg, texto, (x + 12, y + 18), cv2.FONT_HERSHEY_COMPLEX, 0.45, (255, 255, 255), 1)


def processar_imagem(imagem_jpg: np.ndarray, dados_config: tuple) -> np.ndarray:
    x, y, w, h = dados_config['roi']['x'], dados_config['roi']['y'], dados_config['roi']['w'], dados_config['roi']['h']
    boa_lower = np.array(dados_config['cor_boa']['lower_good'])
    boa_upper = np.array(dados_config['cor_boa']['upper_good'])
    ruim_lower = np.array(dados_config['cor_ruim']['lower_bad'])
    ruim_upper = np.array(dados_config['cor_ruim']['upper_bad'])

    filtro_escolhido = dados_config['imagem_analisada']['filtro']

    roi = imagem_jpg[y: y + h, x: x + w]
    roi_blur = cv2.GaussianBlur(roi, (5, 5), 0)
    roi_unsharping = cv2.addWeighted(roi, 1.5, roi_blur, -0.5, 0)

    if filtro_escolhido == "Blur":
        hsv = cv2.cvtColor(roi_blur, cv2.COLOR_BGR2HSV)
        print("hsv = blur")
    if filtro_escolhido == "Unsharping Mask":
        hsv = cv2.cvtColor(roi_unsharping, cv2.COLOR_BGR2HSV)
        print("hsv = unsharping mask")
    else:
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        print("hsv = no filter")

    mask_good = cv2.inRange(hsv, boa_lower, boa_upper)
    mask_bad = cv2.inRange(hsv, ruim_lower, ruim_upper)

    kernel = np.ones((5, 5), np.uint8)

    if filtro_escolhido == "Morphology":
        mask_apply_good = cv2.morphologyEx(mask_good, cv2.MORPH_OPEN, kernel)
        mask_apply_good = cv2.morphologyEx(mask_apply_good, cv2.MORPH_CLOSE, kernel)

        mask_apply_bad = cv2.morphologyEx(mask_bad, cv2.MORPH_OPEN, kernel)
        mask_apply_bad = cv2.morphologyEx(mask_apply_bad, cv2.MORPH_CLOSE, kernel)

        print("mask = morphology\n")
    elif filtro_escolhido == "Erosion":
        mask_apply_good = cv2.erode(mask_good, kernel, iterations=1)

        mask_apply_bad = cv2.erode(mask_bad, kernel, iterations=1)

        print("mask = erosion\n")
    else:
        mask_apply_good = mask_good

        mask_apply_bad = mask_bad

        print("mask = no filter\n")

    pixels_bons = cv2.countNonZero(mask_apply_good)
    pixels_ruins = cv2.countNonZero(mask_apply_bad)
    total_analisado = pixels_bons + pixels_ruins

    print(f"Pixels bons: {pixels_bons}\n")
    print(f"Pixels ruins: {pixels_ruins}\n")
    print(f"Total Pixels: {total_analisado}\n")

    status = "Aguardando..."
    cor_texto = (200, 200, 200)

    if total_analisado > 100:
        porcentagem_total = (pixels_bons / total_analisado) * 100

        print("----- Resultados -----")

        print(f"Porcentagem: {porcentagem_total:.2f}%\n")
    else:
        print("Não há pixels suficientes analisados.\n")

    criar_gauge_dinamica(imagem_jpg, porcentagem_total)
    cv2.rectangle(imagem_jpg, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(imagem_jpg, f"ROI", (x + 65, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 2)

    return imagem_jpg
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", default="grass_img.jpg", help="Caminho da imagem")
    args = parser.parse_args()
    imagem_jpg = cv2.imread(args.img)

    if imagem_jpg is None:
        print("Erro ao carregar imagem.\n")
        exit()

    try:
        with open('config_img.json', 'r') as arq:
            dados_config = json.load(arq)
    except FileNotFoundError:
        print("Erro: Arquivo 'config_img.json' não encontrado.\n")
        exit()

    try:
        while True:
            frame_analisado = processar_imagem(imagem_jpg, dados_config)
            cv2.imshow('Imagem Original', imagem_jpg)
            cv2.imshow('Imagem Analisada', frame_analisado)

            print("Pressione 'Esc' para sair da tela de monitoramento.\n")
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()