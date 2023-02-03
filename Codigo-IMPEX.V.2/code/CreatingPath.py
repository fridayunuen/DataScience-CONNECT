import Directory as Dir
import os

# get user name
user = os.getlogin()

opcion1 = r"C:\\Users\\"+user+r"\\SERVICIOS SHASA S DE RL DE CV\Administrador - Fotografías Subir Pagina\\CONNECT\\TODOS_LOS_TAMANOS"
opcion2 = r"C:\\Users\\"+user+r"\\OneDrive - SERVICIOS SHASA S DE RL DE CV\\Fotografías Subir Pagina\\CONNECT\\TODOS_LOS_TAMANOS"
#opcion1  = r"C:\Users\fcolin\SERVICIOS SHASA S DE RL DE CV\Administrador - Fotografías Subir Pagina\PRUEBAS WEBP\PRUEBAS MAQUINA"

os.chdir(Dir.carpeta_intupt)
if os.path.exists(opcion1):
    with open("path.txt", "w") as f:
        f.write(opcion1)
elif os.path.exists(opcion2):
    with open("path.txt", "w") as f:
        f.write(opcion2)
else: 
    print("La carpeta Drive Shooting no existe... ")    
    print("Fotografías Subir Pagina\\CONNECT\\TODOS_LOS_TAMANOS")
    exit()    
    
