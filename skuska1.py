import paramiko

def get_cpu_usage(ip, username, password):
    try:
        # Vytvorenie SSH klienta
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Pripojenie k zariadeniu
        print(f"Pripájam sa na {ip}...")
        ssh_client.connect(hostname=ip, username=username, password=password)
        
        # Spustenie príkazu na zistenie vyťaženia CPU
        command = "/system/resource/print"
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Spracovanie výstupu
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"Chyba pri spúšťaní príkazu: {error}")
        else:
            print("Výstup príkazu:")
            print(output)

    except paramiko.AuthenticationException:
        print("Chyba: Nesprávne prihlasovacie údaje.")
    except paramiko.SSHException as e:
        print(f"Chyba SSH pripojenia: {e}")
    except Exception as e:
        print(f"Neočakávaná chyba: {e}")
    finally:
        # Uzavretie pripojenia
        ssh_client.close()
        print("Pripojenie bolo uzavreté.")

if __name__ == "__main__":
    # Zadajte IP adresu, používateľské meno a heslo
    ip_address = input("Zadajte IP adresu MikroTiku: ")
    username = input("Zadajte používateľské meno: ")
    password = input("Zadajte heslo: ")

    # Zavolanie funkcie
    get_cpu_usage(ip_address, username, password)