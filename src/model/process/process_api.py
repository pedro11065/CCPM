from flask import Flask, request, jsonify
from src.model.registers.RegisterBill import *
import google.generativeai as genai
import json, os, base64, uuid
from datetime import datetime
import calendar

# Configuração da API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBFe0IwRlSAVfQBf3td4sBx69l_-3eIqic")
genai.configure(api_key=GEMINI_API_KEY)

UPLOAD_FOLDER = r"C:\Users\UXK\OneDrive - QlikTech Inc\Documents\Pedro\CCPM\data"


def load_file(data):
    """
    Carrega arquivo enviado em base64 e o salva no disco.
    Retorna o caminho do arquivo salvo.
    """
    print("Loading file...")
    
    filename = data.get('filename')
    filedata = data.get('data')  # Deve ser um dataURL: "data:image/png;base64,..."
    filetype = data.get('filetype')

    if not filename or not filedata:
        return None, jsonify({'success': False, 'error': 'filename ou data ausente'}), 400

    # Remove prefixo do DataURL e decodifica
    if ',' in filedata:
        header, b64data = filedata.split(',', 1)
    else:
        b64data = filedata
    
    try:
        file_bytes = base64.b64decode(b64data)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Cria a pasta se não existir
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Salva o arquivo
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        print(f"File saved: {file_path}")

        return analyse_data(file_path)

        #return file_path, jsonify({'success': True, 'filename': filename, 'filepath': file_path}), 200

    except Exception as e:
        print(f"Error loading file: {e}")
        return None, jsonify({'success': False, 'error': str(e)}), 400


def analyse_bill(file_path):
    """
    Analisa uma foto de fatura/conta e extrai:
    - valor (amount)
    - data (date)
    - localização (location)
    
    Retorna os dados em formato JSON.
    """
    if not file_path or not os.path.exists(file_path):
        return {
            'ok': False,
            'status': f'Arquivo não encontrado: {file_path}',
            'filepath': file_path
        }

    error_msg = None
    bill_data = None

    try:
        # Determina o tipo MIME baseado na extensão
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.pdf': 'application/pdf',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')

        print(f"Analyzing bill image: {file_path} ({mime_type})")

        # Lê o arquivo
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        # Faz a requisição ao Gemini com prompt específico para faturas
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([
            {
                'mime_type': mime_type,
                'data': file_bytes
            },
            """Analise esta imagem de fatura/conta e extraia APENAS em formato JSON válido (sem markdown, sem texto extra).

        Retorne EXATAMENTE esta estrutura JSON:
        {
            "nome":"nome da empresa provedora (Somente a primeira letra maiuscula)",
            "valor": "valor numérico em reais (ex: 150.50) ou null se não encontrado",
            "data": "data no formato DD/MM/YYYY ou null se não encontrado",
            "localizacao": "cidade, estado ou endereço ou null se não encontrado",
            "tipo_conta": "Com base nas informações da conta defina: Home/Market/Leisure/Cloth/Restaurant/Public transport/Private transport/Studies/Digital/Health/Street food/Other",
            "empresa": "nome da empresa provedora ou null"
        }

        IMPORTANTE:
        - Responda SOMENTE com JSON válido
        - Se não conseguir encontrar um valor, use null
        - Para valor, extraia apenas o número (ex: 150.50, não "R$ 150,50")
        - Para data, retorne em DD/MM/YYYY
        - Para localização, use endereço ou cidade+estado se disponível"""
        ])

        print(f"Response received: {response.text}")

        # Tenta parsear a resposta como JSON
        try:
            # Remove possíveis marcadores de código markdown
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            bill_data = json.loads(response_text)
            print(f"Parsed bill data: {bill_data}")

        except json.JSONDecodeError as je:
            error_msg = f"JSON parsing error: {je}"
            print(error_msg)
            bill_data = {
                "raw_response": response.text,
                "note": "Response was not in JSON format"
            }
            return {
                'ok': False,
                'status': error_msg,
                'filepath': file_path,
                'bill': bill_data
            }

        # Parse date - try both DD/MM/YYYY and YYYY-MM-DD formats
        date_str = bill_data.get("data")
        parsed_date = None
        if date_str:
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
        
        if not parsed_date:
            parsed_date = datetime.today()
            print(f"Could not parse date '{date_str}', using today: {parsed_date}")

        # Parse value - handle null and string formats
        valor_str = bill_data.get("valor")
        if valor_str and valor_str.lower() != "null":
            try:
                valor = float(str(valor_str).replace(",", "."))
            except ValueError:
                valor = 0.0
                error_msg = f"Could not parse valor: {valor_str}"
        else:
            valor = 0.0
            error_msg = "Valor is null or missing"

        db = Db()     
        debtor_id = "10108455-1f99-44a5-a09e-5f7673e9bab9"

        # Create the bill
        print(f"Creating bill with: debtor_id={debtor_id}, name={bill_data.get('nome')}, date={parsed_date}, value={valor}")
        
        success = db.bill.create(
            debtor_id=debtor_id,
            name=bill_data.get("nome", "Fatura"),
            date=parsed_date,
            value=valor,
            installment=1,
            installment_value=valor,
            remaining_installments=0,  # Should be 1 for installment=1
            remaining=0,
            subscription=False
        )

        if success:
            return {
                'ok': True,
                'filename': os.path.basename(file_path),
                'filepath': file_path,
                'bill': bill_data,
                'status': "Bill registered successfully"
            }
        else:
            return {
                'ok': False,
                'status': 'Database insertion failed',
                'filepath': file_path,
                'bill': bill_data
            }

    except Exception as e:
        print(f"Error analyzing bill: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'ok': False,
            'status': str(e),
            'filepath': file_path,
            'bill': bill_data
        }


def analyse_data(file_path):
    """
    Analisa uma imagem genérica usando Gemini API.
    Retorna análise em formato JSON.
    (Mantido para compatibilidade)
    """
    return analyse_bill(file_path)