
BANKS = [("Inter","*1468",9),("PagBank","*3298",15),("Mercado Pago","*3339",6),("Casas Bahia","*6889",6)]

banco = "PagBank"
data_transacao = '16/12/2025'

data_transacao = data_transacao.split("/")
for dadosBanco, j in enumerate(data_transacao):
    data_transacao[dadosBanco] = int(j)

print(data_transacao)


for dadosBanco in BANKS:
    if dadosBanco[0]==banco:
        print(banco)
        if data_transacao[0]<=dadosBanco[2]:
            data_transacao[0]=dadosBanco[2]
            print("A")
        elif data_transacao[0]>dadosBanco[2] and data_transacao[1]<12:
            data_transacao[0]=dadosBanco[2]
            data_transacao[1]=data_transacao[1]+1
            print("B")
        elif data_transacao[0]>dadosBanco[2] and data_transacao[1]==12:
            data_transacao[0]=dadosBanco[2]
            data_transacao[1]=1
            data_transacao[2]=data_transacao[2]+1
            print("C")

data_transacao = f"{data_transacao[2]}/{data_transacao[1]}/{data_transacao[0]} 00:00:00"

print(data_transacao)

# if dt:
#     try:
#         # convert DD/MM/YYYY -> YYYY-MM-DD
#         if "/" in dt:
#             parts = dt.split("/")
#             if len(parts) == 3:
#                 dt = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
#         # add time if only date provided
#         if len(dt) == 10:
#             dt = f"{dt} 00:00:00"
#     except Exception:
#         pass
 
