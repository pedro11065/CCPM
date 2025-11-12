from flask import jsonify
import google.generativeai as genai
from src.model.services.Qapp import *
#from src.model import Db
import json, os, base64
from datetime import datetime

# Configuração da API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBFe0IwRlSAVfQBf3td4sBx69l_-3eIqic") ; genai.configure(api_key=GEMINI_API_KEY)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
types = ["Home","Market","Leisure","Cloth","Restaurant","Public transport","Private transport","Studies","Digital","Health","Street food","Other"]
banks = ["Inter","Pagbank"]


def billInfo():

    from src.model import Db
    db = Db()
    debtors = db.dbDebtors

    for i, debtor in enumerate(debtors): print(f"{i+1} - {debtor[1]}")
    debtor = input("\nWho are you going to pay?: ") ; os.system("cls")
    debtor_id = debtors[int(debtor)-1][0] ; print(debtor) ; os.system("cls")
    debtor_name = debtors[int(debtor)-1][1] ; print(debtor) ; os.system("cls")
    debtor_limit = debtors[int(debtor)-1][2] ; print(debtor) ; os.system("cls")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    name = input("What you bought?: ") ; os.system("cls")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    date = datetime.strptime(input("Quando será o primeiro pagamento? (DD/MM/YYYY): "), "%d/%m/%Y"); os.system("cls")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    value = float(input("How much?: ")) ; os.system("cls")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    installment = int(input("How much installments?")) ; os.system("cls")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  
    localization = input("Where?(city): ") ; os.system("cls") #COORDENADAS
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    place = input("Where?(place): ") ; os.system("cls")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    for i, type in enumerate(types): print(f"{i+1} - {type[1]}")
    type = input("What type of account??: ") ; os.system("cls")
    type = types[int(type)-1]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    subscription = input("Its a subscription?? (s/n): ").strip().lower()
    if subscription in ("s", "sim", "y", "yes"):
        subscription=True
    else:
        subscription=False
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    installment_value = value/installment 
    remaining_installments = installment
    remaining = value

    db.dbBill.create(debtor_id, name, date, value, installment, installment_value, remaining_installments, remaining, subscription, localization, debtor_name, place, type)


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def analyseBill(data):
    """
    Carrega arquivo enviado em base64 e o salva no disco.
    Retorna o caminho do arquivo salvo.
    """
    print("Loading file...")
    
    filename = data.get('filename')
    filedata = data.get('data')  # Deve ser um dataURL: "data:image/png;base64,..."
    filetype = data.get('filetype')

    if not filename or not filedata:
        return jsonify({'ok': False, 'error': 'filename ou data ausente'}), 400

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
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'ok': False, 'status': f'Erro ao salvar arquivo: {str(e)}'}), 400

    if not file_path or not os.path.exists(file_path):
        return jsonify({
            'ok': False,
            'status': f'Arquivo não encontrado: {file_path}',
            'filepath': file_path
        }), 400

    # GEMINI \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    bill_data = None
    
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

    # Lê o arquivo
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content([
        {
            'mime_type': mime_type,
            'data': file_bytes
        },
        f"""Analise esta imagem de fatura/conta e extraia APENAS em formato JSON válido (sem markdown, sem texto extra).

        Retorne EXATAMENTE esta estrutura JSON:
        {{
            "nome":"nome da empresa provedora (Somente a primeira letra maiuscula)",
            "valor": "valor numérico em reais (ex: 150.50) ou null se não encontrado",
            "data": "data no formato DD/MM/YYYY ou null se não encontrado",
            "localizacao": "endereço da empresa no qual o usuário fez o pagamento
                (Caso somente contenha informações referentes ao nome empresa, 
                pesquisar pelo endreço da mesma) ou cidade que o usuário fez o pagamento ou null se não encontrado",
            "tipo_conta": "Com base nas informações escolha uma das opções: {types}",
            "empresa": "nome da empresa provedora ou null",
            "banco": "em que banco a transação foi efetuada: {banks}"
        }}

        IMPORTANTE:
        - Responda SOMENTE com JSON válido
        - Se não conseguir encontrar um valor, use null
        - Para valor, extraia apenas o número (ex: 150.50, não "R$ 150,50")
        - Para data, retorne em DD/MM/YYYY
        - Para localização, use endereço ou cidade+estado se disponível"""
    ])

    print(f"Response received: {response.text}")

    # Parse JSON response
    response_text = response.text.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    bill_data = json.loads(response_text)


    # DATABASE \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    try:
        from src.model import Db
        db = Db()
        
        debtor_id = "10108455-1f99-44a5-a09e-5f7673e9bab9"        # Validate and convert data types safely
        try:
            date_value = datetime.strptime(bill_data.get("data", "01/01/2025"), "%d/%m/%Y")
        except (ValueError, TypeError):
            date_value = datetime.now()  # fallback to current date
            
        try:
            valor_str = str(bill_data.get("valor", "0")).replace(",", ".")
            value = float(valor_str) if valor_str != "null" and valor_str else 0.0
        except (ValueError, TypeError):
            value = 0.0

        success = db.bill.create(
            debtor_id=debtor_id,
            name=bill_data.get("nome", "Fatura"),
            date=date_value,
            value=value,
            installment=1,
            installment_value=value,
            remaining_installments=1,
            remaining=value,
            subscription=False,
            localization=bill_data.get("localizacao"),
            bank=bill_data.get("banco"),
            place=bill_data.get("empresa"),
            type=bill_data.get("tipo_conta"),
        )

        if success:

            reloadApp()

            return jsonify({
                'ok': True,
                'filename': os.path.basename(file_path),
                'filepath': file_path,
                'bill': bill_data,
                'status': "Bill registered successfully"
            }), 201
        else:
            return jsonify({
                'ok': False,
                'status': 'Database insertion failed',
                'filepath': file_path,
                'bill': bill_data
            }), 500

    except Exception as e:
        print(f"Error inserting bill to database: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'ok': False,
            'status': f'Database error: {str(e)}',
            'filepath': file_path,
            'bill': bill_data
        }), 500
