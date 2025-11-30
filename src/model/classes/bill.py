from flask import jsonify
import google.generativeai as genai
from src.model.services.Qapp import *
from src.config.colors import *
#from src.model import Db
import json, os, base64, traceback
from datetime import datetime

# Configuração da API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBFe0IwRlSAVfQBf3td4sBx69l_-3eIqic") ; genai.configure(api_key=GEMINI_API_KEY)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/receipts")

TYPES = ["Home","Market","Leisure","Cloth","Restaurant","Public transport","Private transport","Studies","Digital","Health","Street food","Other"]
BANKS = [("Inter","*1468","9"),("Pagbank","**3298","15"),("Mercado Pago","**3339","6")]

class Bill:

    @staticmethod
    def load_image(data):
        """
        Carrega arquivo enviado em base64 e o salva no disco.
        Retorna o caminho do arquivo salvo.
        """
        print(cyan("[back-end]: ") + "loading file...")
        
        filename = data.get('filename')
        filedata = data.get('data')  # Deve ser um dataURL: "data:image/png;base64,..."
        filetype = data.get('filetype')

        if not filename or not filedata:
            print(red("[ERROR]: ") + "No file was founded.")
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

            print(cyan("[back-end]: ") + f"File saved: {file_path}")

            
        except Exception as e:
            print(red("[ERROR]: ") + f"Error saving file: {e}")
            return jsonify({'ok': False, 'status': f'Erro ao salvar arquivo: {str(e)}'}), 400

        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'ok': False,
                'status': f'Arquivo não encontrado: {file_path}',
                'filepath': file_path
            }), 400
        
        return file_path
        

    def credit(self, data, photo):

        if photo:

            file_path = self.load_image(data)

            # GEMINI \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

            bill_data = None

            print(cyan("[back-end]: ") + "reading file...")
            
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

            model = genai.GenerativeModel('gemini-2.5-pro')
            response = model.generate_content([
                {
                    'mime_type': mime_type,
                    'data': file_bytes
                },
                f"""Analise este comprovante de uma compra no crédito e extraia APENAS em formato JSON válido (sem markdown, sem texto extra).

                Retorne EXATAMENTE esta estrutura JSON:
                {{
                    "nome":"nome da empresa provedora (Somente a primeira letra maiuscula)",
                    "valor": "valor numérico em reais (ex: 150.50) ou null se não encontrado",
                    "data": "data no formato AAAA-MM-DD HH:MM:SS ou null se não encontrado. Se a data da compra passar o dia limite do cartão {BANKS}, adicione 1 mês data",
                    "localizacao": "cidade que o usuário fez o pagamento(somente a cidade) ou null se não encontrado",
                    "tipo_conta": "Com base nas informações escolha uma das opções: {TYPES}",
                    "empresa": "nome da empresa provedora(Somente a primeira letra maiuscula) ou null",
                    "cartao": "em que cartão a transação foi efetuada: {BANKS} (SOMENTE O NOME DO CARTÃO STR); "
                    "parcelas": "Quantidade de parcelas";
                }}

                IMPORTANTE:
                - Responda SOMENTE com JSON válido
                - Se não conseguir encontrar um valor, use null
                - Para valor, extraia apenas o número (ex: 150.50, não "R$ 150,50")
                - Para data, retorne em YYYY-MM-DD HH:MM:SS
                - Para localização, use endereço ou cidade+estado se disponível"""
            ])

            print(cyan("[back-end]: ") + "File was read.")
            # print(cyan("[back-end]: ") + "Data founded:")
            # print(f"{response.text}")

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

        else: 
            
            bill_data = {
                "nome": data.get("name") or data.get("nome"),
                "valor": data.get("value") or data.get("valor"),
                "data": data.get("date") or data.get("data"),
                "localizacao": data.get("location") or data.get("localizacao"),
                "tipo_conta": data.get("category") or data.get("tipo") or data.get("tipo_conta"),
                "empresa": data.get("company") or data.get("empresa"),
                "cartao": data.get("card") or data.get("cartao"),
                "parcelas": data.get("installments") or data.get("parcelas") or 1
            }

            # Normalize date to 'YYYY-MM-DD HH:MM:SS' where possible
        
            data_transacao=bill_data("data").split("/")
            for dadosBanco, j in enumerate(data_transacao):
                data_transacao[dadosBanco] = int(j)

            for BankData in BANKS:
                if BankData[0]==bill_data.get("cartao"):
                    if data_transacao[0]<=BankData[2]:
                        data_transacao[0]=BankData[2]
                        print("A")
                    elif data_transacao[0]>BankData[2] and data_transacao[1]<12:
                        data_transacao[0]=BankData[2]
                        data_transacao[1]=data_transacao[1]+1
                        print("B")
                    elif data_transacao[0]>BankData[2] and data_transacao[1]==12:
                        data_transacao[0]=BankData[2]
                        data_transacao[1]=1
                        data_transacao[2]=data_transacao[2]+1
                        print("C")

            bill_data["data"] = f"{data_transacao[2]}-{data_transacao[1]}-{data_transacao[0]} 00:00:00"
            
            
        lat = data.get("latitude")
        lng = data.get("longitude")
        coordinates = f"{lat}, {lng}" if lat and lng else None

            
        # DATABASE \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        if bill_data.get("cartao") == "Casas Bahia":
            debtor_id = "aa2a7f8c-ad7d-4813-ad40-6ac481b56dd1" 
        elif bill_data.get("cartao") == "Inter":
            debtor_id = "87d68d70-e7d5-4a60-a6eb-2b27b9bbefe6" 
        elif bill_data.get("cartao") == "Mercado Pago":
            debtor_id = "d6229403-99ad-44c5-82c0-f1cde2495207" 
        elif bill_data.get("cartao") == "PagBank":
            debtor_id = "2c589c1c-e034-1250-9827-bf1f793b72b9"
        else: debtor_id = "10108455-1f99-44a5-a09e-5f7673e9bab9"  

        try:
            from src.model import Db
            db = Db()
            
            # Validate and convert data types safely
            date_value = bill_data.get("data")
        
            try:
                valor_str = str(bill_data.get("valor", "0")).replace(",", ".")
                value = float(valor_str) if valor_str != "null" and valor_str else 0.0
                
            except (ValueError, TypeError):
                value = 0.0

            # Safely parse parcelas
            raw_parcelas = bill_data.get("parcelas")
            try:
                parcelas = int(str(raw_parcelas).strip())
                if parcelas <= 0:
                    parcelas = 1
            except Exception:
                parcelas = 1

            per_installment = value / parcelas if parcelas else value

            print(cyan("[back-end]: ") + "Registering bill...")

            success = db.bill.create(
                debtor_id=debtor_id,
                name=bill_data.get("nome"),
                date=date_value,
                value=value,
                installment=parcelas,
                installment_value=per_installment,
                remaining_installments=parcelas,
                remaining=value,
                subscription=False,
                localization=bill_data.get("localizacao"),
                coordinates=coordinates,
                bank=bill_data.get("cartao"),
                place=bill_data.get("empresa"),
                type=bill_data.get("tipo_conta"),
                credit = True
            )

        except Exception as e:

            print(red("[ERROR]: ") + f"Error inserting bill to database: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'ok': False,
                'status': f'Database error: {str(e)}',
                'bill': bill_data
            }), 500


        if success:
            reloadAppAsync()

            print(cyan("[back-end]: ") + "Bill registered successfully!")
            return jsonify({
            'ok': True,
            'bill': bill_data,
            'status': "Bill registered successfully"
            }), 201


        if not success:

            print(red("[ERROR]: ") + f"Error inserting bill to database.")
            return jsonify({
                'ok': False,
                'status': 'Database insertion failed',
                'bill': bill_data
            }), 500






    def debit(self, data, photo):
        
        file_path = self.load_image(data)

        # GEMINI \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        bill_data = None

        if photo:

            print(cyan("[back-end]: ") + "reading file...")
            
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
                    "data": "data no formato AAAA-MM-DD HH:MM:SS ou null se não encontrado",
                    "localizacao": "cidade que o usuário fez o pagamento(somente a cidade) ou null se não encontrado",
                    "tipo_conta": "Com base nas informações escolha uma das opções: {TYPES}",
                    "empresa": "nome da empresa provedora(Somente a primeira letra maiuscula) ou null",
                    "cartao": "em que cartão a transação foi efetuada: {BANKS}"
                }}

                IMPORTANTE:
                - Responda SOMENTE com JSON válido
                - Se não conseguir encontrar um valor, use null
                - Para valor, extraia apenas o número (ex: 150.50, não "R$ 150,50")
                - Para data, retorne em DD/MM/YYYY
                - Para localização, use endereço ou cidade+estado se disponível"""
            ])

            print(cyan("[back-end]: ") + "File was read.")
            # print(cyan("[back-end]: ") + "Data founded:")
            # print(f"{response.text}")

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

        else:
            # Normalize incoming payload into the same shape used when OCR/AI is used
            bill_data = {
                "type": data.get('type'),
                "nome": data.get('name') or data.get('nome'),
                "valor": data.get('value') or data.get('valor'),
                # keep date as provided (expected formats: YYYY-MM-DD or DD/MM/YYYY)
                "data": data.get('date') or data.get('data'),
                "localizacao": data.get('location') or data.get('localizacao'),
                "tipo_conta": data.get('category') or data.get('tipo_conta'),
                "empresa": data.get('company') or data.get('empresa'),
                # optional card field
                "cartao": data.get('card') or data.get('cartao')
            }
            #print(cyan("[back-end]: ") + f"Using provided bill data: {bill_data}")
            
        coordinates=data.get("latitude") + ", " + data.get("longitude")



        # DATABASE \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        try:
            from src.model import Db
            db = Db()
            
            debtor_id = "10108455-1f99-44a5-a09e-5f7673e9bab9"        # Validate and convert data types safely
            date_value = bill_data.get("data")
        
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
                coordinates=coordinates,
                bank=bill_data.get("cartao"),
                place=bill_data.get("empresa"),
                type=bill_data.get("tipo_conta"),
                credit = False
            )

            if success:

                reloadAppAsync()

                print(cyan("[back-end]: ") + "Bill registered successfully!")
                return jsonify({
                    'ok': True,
                    'bill': bill_data,
                    'status': "Bill registered successfully"
                }), 201
            else:

                print(red("[ERROR]: ") + f"Error inserting bill to database.")
                return jsonify({
                    'ok': False,
                    'status': 'Database insertion failed',
                    'bill': bill_data
                }), 500

        except Exception as e:

            print(red("[ERROR]: ") + f"Error inserting bill to database: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'ok': False,
                'status': f'Database error: {str(e)}',
                'bill': bill_data}), 500
