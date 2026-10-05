import cv2
import numpy as np
import json
import sys
from deepmerge import merge_or_raise
import argparse

def criar_trackbars(nome_janela: str):
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, 400, 250)

    def nothing(x): pass

    cv2.createTrackbar('H_min', nome_janela, 0, 179, nothing)
    cv2.createTrackbar('S_min', nome_janela, 0, 255, nothing)
    cv2.createTrackbar('V_min', nome_janela, 0, 255, nothing)
    cv2.createTrackbar('H_max', nome_janela, 179, 179, nothing)
    cv2.createTrackbar('S_max', nome_janela, 255, 255, nothing)
    cv2.createTrackbar('V_max', nome_janela, 255, 255, nothing)

def ler_trackbars(nome_janela: str) -> tuple:
    h_min = cv2.getTrackbarPos('H_min', nome_janela)
    s_min = cv2.getTrackbarPos('S_min', nome_janela)
    v_min = cv2.getTrackbarPos('V_min', nome_janela)
    h_max = cv2.getTrackbarPos('H_max', nome_janela)
    s_max = cv2.getTrackbarPos('S_max', nome_janela)
    v_max = cv2.getTrackbarPos('V_max', nome_janela)
    return [h_min, s_min, v_min], [h_max, s_max, v_max]
    
def criar_menus(filtro_dict: dict, tentativas = 1, max_tentativas = 3) -> int:
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

    return numero_selecionado

def calibrar_cor(titulo_janela: str, roi_imagem: np.ndarray, num_filtro: int) -> tuple:
    print(f"Ajuste os controles até o que for desejado ficar branco na janela {titulo_janela}.")
    print("Pressione 'Esc' para sair da tela de edição...\n")
    criar_trackbars('Controles')

    while True:
        hsv = cv2.cvtColor(roi_imagem, cv2.COLOR_BGR2HSV)

        lower_bound, upper_bound = ler_trackbars('Controles')

        mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))

        kernel = np.ones((5, 5), np.uint8)

        if num_filtro == 1:
            mask_morfologia_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask_apply = cv2.morphologyEx(mask_morfologia_open, cv2.MORPH_CLOSE, kernel)
        elif num_filtro == 2:
            mask_apply = cv2.erode(mask, kernel, iterations=1)
        else:
            mask_apply = mask

        result = cv2.bitwise_and(roi_imagem, roi_imagem, mask=mask_apply)

        cv2.imshow(titulo_janela, mask_apply)
        cv2.imshow('Imagem Original', result)
            
        if cv2.waitKey(1) & 0xFF == 27:
            cv2.destroyWindow(titulo_janela)
            cv2.destroyWindow('Controles')
            return lower_bound, upper_bound
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", default="grass_img.jpg", help="Caminho da imagem")
    args = parser.parse_args()
    img = cv2.imread(args.img)

    if img is None:
        print("Erro ao carregar imagem ou imagem indisponível!")
        sys.exit()

    imagem_blur = cv2.GaussianBlur(img, (3, 3), 0)
    imagem_nitida = cv2.addWeighted(img, 1.5, imagem_blur, -0.5, 0)

    filtro_dict = {
        1: {"text_cor_boa": "Calibrar cor boa com filtro Morphology", "text_cor_ruim": "Calibrar cor ruim com filtro Morphology", "imagem_analisada": img},
        2: {"text_cor_boa": "Calibrar cor boa com filtro Erosion", "text_cor_ruim": "Calibrar cor ruim com filtro Erosion", "imagem_analisada": img},
        3: {"text_cor_boa": "Calibrar cor boa com filtro Blur", "text_cor_ruim": "Calibrar cor ruim com filtro Blur", "imagem_analisada": imagem_blur},
        4: {"text_cor_boa": "Calibrar cor boa com filtro Unsharping Mask", "text_cor_ruim": "Calibrar cor ruim com filtro Unsharping Mask", "imagem_analisada": imagem_nitida},
        5: {"text_cor_boa": "Calibrar cor boa sem filtro", "text_cor_ruim": "Calibrar cor ruim sem filtro", "imagem_analisada": img}
    }

    numero_selecionado = criar_menus(filtro_dict)

    # frame_dict = {
    #    1: {"imagem_analisada": img},
    #    2: {"imagem_analisada": img},
    #    3: {"imagem_analisada": imagem_blur},
    #    4: {"imagem_analisada": imagem_nitida},
    #    5: {"imagem_analisada": img}
    # }

    # try:
    #    result_dict = merge_or_raise.merge(filtro_dict, frame_dict)
    # except Exception as e:
    #    print(f"Erro ao unificar dicionários: {e}")

    text_cor_boa = filtro_dict[numero_selecionado]["text_cor_boa"]
    text_cor_ruim = filtro_dict[numero_selecionado]["text_cor_ruim"]
    imagem_analisada = filtro_dict[numero_selecionado]["imagem_analisada"]

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

    try:
        cor_boa_lower, cor_boa_upper = calibrar_cor(text_cor_boa, roi, numero_selecionado)
        cor_ruim_lower, cor_ruim_upper = calibrar_cor(text_cor_ruim, roi, numero_selecionado)
        
        config = {
            "roi": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
            "cor_boa": {"lower_good": cor_boa_lower, "upper_good": cor_boa_upper},
            "cor_ruim": {"lower_bad": cor_ruim_lower, "upper_bad": cor_ruim_upper}
        }

        with open('config_img.json', 'w') as arquivo:
            json.dump(config, arquivo, indent=4)

        print(f"\nSucesso! As configurações foram salvas no arquivo json.\n")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()