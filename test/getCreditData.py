
BANKS = [("Inter","*1468","9"),("Pagbank","*3298","15"),("Mercado Pago","*3339","6"),("Casas Bahia","6889","")]

banco = ""
dt = '29/11/2025'

dt_split = dt.split("/")
print(dt_split)

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
 
print(dt)