import paramiko

def test(ip, ssh_port, username, password, sudo_pass):
    def get_output(output, error, username):
        if output:
            print(output.strip('\n'))
            return (True, None)
        else:
            if error != f'[sudo] password for {username}: ':
                print(error)
                return (False, error)
            return (True, None)
    # Подключение к удалённому серверу
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=ssh_port, username=username, password=password)

        commands = [
            #здесь должны находится команды для теста, например: 'mkdir папка1'
            ]

    
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            output = stdout.read().decode()
            error = stderr.read().decode()
            otp = get_output(output, error, username)

# Замените 'hostname', 'port', 'username', 'password' на реальные данные сервера
test('hostname', 'port', 'username', 'password', 'sudo_pass')

