import cv2
import numpy as np
import json
import sys
from deepmerge import merge_or_raise

nome_arquivo = "grass.jpg"
imagem = cv2.imread(nome_arquivo)
imagem_blur = cv2.GaussianBlur(imagem, (3, 3), 0)
imagem_nitida = cv2.addWeighted(imagem, 1.5, imagem_blur, -0.5, 0)

tentativas = 1
max_tentativas = 3

filtro_dict = {
    1: {"text_cor_boa": "Calibrar cor boa com filtro Morphology", "text_cor_ruim": "Calibrar cor ruim com filtro Morphology"},
    2: {"text_cor_boa": "Calibrar cor boa com filtro Erosion", "text_cor_ruim": "Calibrar cor ruim com filtro Erosion"},
    3: {"text_cor_boa": "Calibrar cor boa com filtro Blur", "text_cor_ruim": "Calibrar cor ruim com filtro Blur"},
    4: {"text_cor_boa": "Calibrar cor boa com filtro Unsharping Mask", "text_cor_ruim": "Calibrar cor ruim com filtro Unsharping Mask"},
    5: {"text_cor_boa": "Calibrar cor boa sem filtro", "text_cor_ruim": "Calibrar cor ruim sem filtro"}
}

frame_dict = {
    1: {"imagem_analisada": imagem},
    2: {"imagem_analisada": imagem},
    3: {"imagem_analisada": imagem_blur},
    4: {"imagem_analisada": imagem_nitida},
    5: {"imagem_analisada": imagem}
}

try:
    result_dict = merge_or_raise.merge(filtro_dict, frame_dict)
except Exception as e:
    print(f"Erro ao unificar dicionários: {e}")

print("\nMenu:\n\n (9) Sair\n\n")
print("Filtro disponíveis:\n\n (1) Morphology\n (2) Erosion\n (3) Blur\n (4) Unsharping Mask\n (5) No filters\n\n")

while tentativas <= max_tentativas:
    try:
        numero_selecionado = int(input(f"[{tentativas}/{max_tentativas}] Selecione uma ação ou filtro que deseja aplicar: "))
        print(f"\nAção/Filtro escolhido: {numero_selecionado}\n")
        if numero_selecionado == 9:
            print("\nEncerrando operação...\n")
            sys.exit()
        if numero_selecionado not in filtro_dict or not filtro_dict[numero_selecionado]:
            print("Filtro não encontrado! Prosseguindo à próxima tentativa...\n")
            tentativas += 1
        else:
            break
    except (TypeError, ValueError):
        numero_selecionado = None
        print("\nDigite um valor válido para selecionar a ação ou filtro desejado.\n")
        tentativas += 1

if numero_selecionado not in filtro_dict or not filtro_dict[numero_selecionado]:
    print(f"Filtro não encontrado após {max_tentativas} tentativas. Finalizando operação...\n")
    sys.exit()

text_cor_boa = result_dict[numero_selecionado]["text_cor_boa"]
text_cor_ruim = result_dict[numero_selecionado]["text_cor_ruim"]
imagem_analisada = result_dict[numero_selecionado]["imagem_analisada"]

if imagem_analisada is None:
    print("Erro ao carregar imagem ou indisponível!")
    sys.exit()

def criar_trackbars(nome_janela):
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, 400, 250)

    def nothing(x): pass

    cv2.createTrackbar('H_min', nome_janela, 0, 179, nothing)
    cv2.createTrackbar('S_min', nome_janela, 0, 255, nothing)
    cv2.createTrackbar('V_min', nome_janela, 0, 255, nothing)
    cv2.createTrackbar('H_max', nome_janela, 179, 179, nothing)
    cv2.createTrackbar('S_max', nome_janela, 255, 255, nothing)
    cv2.createTrackbar('V_max', nome_janela, 255, 255, nothing)

def ler_trackbars(nome_janela):
    h_min = cv2.getTrackbarPos('H_min', nome_janela)
    s_min = cv2.getTrackbarPos('S_min', nome_janela)
    v_min = cv2.getTrackbarPos('V_min', nome_janela)
    h_max = cv2.getTrackbarPos('H_max', nome_janela)
    s_max = cv2.getTrackbarPos('S_max', nome_janela)
    v_max = cv2.getTrackbarPos('V_max', nome_janela)
    return [h_min, s_min, v_min], [h_max, s_max, v_max]

print("Iniciando verificação da imagem...")
roi_box = cv2.selectROI("Selecione a área de leitura", imagem_analisada, fromCenter=False)
x, y, w, h = roi_box

cv2.destroyWindow("Selecione a área de leitura")

if w > 0 and h > 0:
    roi = imagem_analisada[y: y + h, x: x + w]
    print(f"\nCoordenandas selecionadas para a ROI: roi = imagem [{y}: {y+h}, {x}: {x+w}]\n")
else:
    roi = imagem_analisada
    print("Nenhum recorte para a ROI")

print("Ajuste os controles até o que for desejado ficar branco.")
print("Pressione 'Esc' para sair da tela de edição...\n")
criar_trackbars('Controles')

while True:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_bound_good, upper_bound_good = ler_trackbars('Controles')

    mask = cv2.inRange(hsv, np.array(lower_bound_good), np.array(upper_bound_good))

    kernel = np.ones((5, 5), np.uint8)

    if numero_selecionado == 1:
        mask_morfologia_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask_apply = cv2.morphologyEx(mask_morfologia_open, cv2.MORPH_CLOSE, kernel)
    elif numero_selecionado == 2:
        mask_apply = cv2.erode(mask, kernel, iterations=1)
    else:
        mask_apply = mask

    result_good = cv2.bitwise_and(roi, roi, mask=mask_apply)

    cv2.imshow(text_cor_boa, mask_apply)
    cv2.imshow('Imagem original', result_good)
        
    if cv2.waitKey(1) & 0xFF == 27:
        cor_boa_lower, cor_boa_upper = lower_bound_good, upper_bound_good
        break

cv2.destroyWindow(text_cor_boa)
cv2.destroyWindow('Controles')

print("Ajuste os controles até o que for indesejado ficar branco.")
print("Pressione 'Esc' para sair da tela de edição...\n")
criar_trackbars('Controles')

while True:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_bound_bad, upper_bound_bad = ler_trackbars('Controles')

    mask = cv2.inRange(hsv, np.array(lower_bound_bad), np.array(upper_bound_bad))

    kernel = np.ones((5, 5), np.uint8)

    if numero_selecionado == 1:
        mask_morfologia_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask_apply = cv2.morphologyEx(mask_morfologia_open, cv2.MORPH_CLOSE, kernel)
    elif numero_selecionado == 2:
        mask_apply = cv2.erode(mask, kernel, iterations=1)
    else:
        mask_apply = mask

    result_bad = cv2.bitwise_and(roi, roi, mask=mask_apply)

    cv2.imshow(text_cor_ruim, mask_apply)
    cv2.imshow('Imagem Original', result_bad)

    if cv2.waitKey(1) & 0xFF == 27:
        cor_ruim_lower, cor_ruim_upper = lower_bound_bad, upper_bound_bad
        break

cv2.destroyAllWindows()

config = {
    "roi": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
    "cor_boa": {"lower_good": cor_boa_lower, "upper_good": cor_boa_upper},
    "cor_ruim": {"lower_bad": cor_ruim_lower, "upper_bad": cor_ruim_upper}
}

with open('config_img.json', 'w') as arquivo:
    json.dump(config, arquivo, indent=4)

print(f"\nSucesso! As configurações foram salvas no arquivo json.\n")