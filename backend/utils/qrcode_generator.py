import qrcode
import os
from io import BytesIO
import base64

def generate_qrcode(data, save_path=None):
    """
    Gera um QR code a partir dos dados fornecidos
    
    Args:
        data: String com os dados a serem codificados
        save_path: Caminho para salvar a imagem (opcional)
    
    Returns:
        String base64 da imagem ou caminho do arquivo salvo
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    if save_path:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        return save_path
    else:
        # Retornar como base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

def generate_menu_qrcode(mesa_numero, cardapio_id, base_url):
    """
    Gera QR code para visualização do cardápio de uma mesa
    
    Args:
        mesa_numero: Número da mesa
        cardapio_id: ID do cardápio
        base_url: URL base do frontend
    
    Returns:
        String base64 do QR code
    """
    url = f"{base_url}/cardapio?mesa={mesa_numero}&cardapio={cardapio_id}"
    return generate_qrcode(url)

def generate_table_qrcode_file(mesa_numero, cardapio_id, base_url, output_dir):
    """
    Gera arquivo de QR code para uma mesa
    
    Args:
        mesa_numero: Número da mesa
        cardapio_id: ID do cardápio
        base_url: URL base do frontend
        output_dir: Diretório para salvar o arquivo
    
    Returns:
        Caminho do arquivo gerado
    """
    url = f"{base_url}/cardapio?mesa={mesa_numero}&cardapio={cardapio_id}"
    filename = f"mesa_{mesa_numero}_qrcode.png"
    save_path = os.path.join(output_dir, filename)
    return generate_qrcode(url, save_path)
