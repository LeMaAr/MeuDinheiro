import random

def gerar_cor():
    #  define uma paleta de cores pré-definida, onde cada cor é representada por seu código hexadecimal. 
    # A função random.choice() é usada para selecionar aleatoriamente uma cor da paleta, 
    # garantindo que as categorias criadas tenham cores variadas e visualmente distintas.

    paleta = ["#E83442", "#AD1457", "#6A1B9A", "#4527A0", "#283593", 
              "#1565C0", "#0277BD", "#00838F", "#00695C", "#2E7D32",
              "#558B2F", "#9E9D24", "#F9A825", "#FF8F00", "#D84315", "#ED1111"]
    
    return random.choice(paleta)
