import paramiko

class User:
    def __init__(self, username: str, password: str):
        self.username = username 
        self.password = password


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    def _get_output(self, output, error, username):
        if output:
            print(output.strip('\n'))
            return (True, None)
        else:
            if error != f'[sudo] password for {username}: ':
                print(error)
                return (False, error)
            return (True, None)
    
    def _do_commands(self, User, commands=[] ):
        with paramiko.SSHClient() as ssh:
            sudo_pass = User.password
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, port=self.port, username=User.username, password=User.password)
    
            for command in commands:
                stdin, stdout, stderr = ssh.exec_command(command)
                
                output = stdout.read().decode()
                error = stderr.read().decode()
                otp = self._get_output(output, error, User.username)
    
    def create_user_as_sudo(self, User, user_name):
        sudo_pass = User.password
        commands = [
            f'echo {sudo_pass} | sudo -S adduser --force-badname --disabled-password --gecos "" {user_name}',
            f'echo {sudo_pass} | sudo -S usermod -aG sudo {user_name}',
            f"echo {sudo_pass} | sudo -S -u {user_name} ssh-keygen -t rsa -N '' -f /home/{user_name}/.ssh/id_rsa"
            ]
        self._do_commands(User, commands)

    def disable_ssh_password(self, User):
        sudo_pass = User.password
        commands = [
            f'echo {sudo_pass} | sudo -S cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup',  # Создание резервной копии файла
            f'echo {sudo_pass} | sudo -S sed -i "/^#PasswordAuthentication yes/cPasswordAuthentication no" /etc/ssh/sshd_config',  # Отключение аутентификации по паролю
            f'echo {sudo_pass} | sudo -S systemctl restart sshd'  # Перезапуск сервиса SSH
        ]
        
        self._do_commands(User, commands)
        print('ssh password disabled')

    def install_postgresql(self, User):
        sudo_pass = User.password
        commands = [
            f'echo {sudo_pass} | sudo -S apt-get update',
            f'echo {sudo_pass} | sudo -S apt install -y postgresql postgresql-contrib',
            f'echo {sudo_pass} | sudo -S apt install -y postgresql-common',  
            f'echo {sudo_pass} | sudo -S /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh',
            ]
        
        self._do_commands(User, commands)

    def create_pg_db(self, User, db_name):
        sudo_pass = User.password
        commands = [
            f"echo {sudo_pass} | sudo -S -u postgres psql -c 'CREATE DATABASE {db_name};'",
            ]

        self._do_commands(User, commands)
        
    def create_pg_user(self, User, user_name, user_pass, db_name):
        sudo_pass = User.password
        
        create_user = f'CREATE USER {user_name} WITH PASSWORD ' + f"'{user_pass}';"
        
        commands = [
            f'echo {sudo_pass} | sudo -S -u postgres psql -c  "' + create_user + '"',
            ]
        self._do_commands(User, commands)
        
    def pg_user_give_prvg(self, User, user_name, db_name):
        sudo_pass = User.password
        
        commands = [
            f"echo {sudo_pass} | sudo -S -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {user_name};'",
            ]
        self._do_commands(User, commands)
        
    def pg_user_for_read(self, User, user_name, db_name):
        sudo_pass = User.password
        commands = [
            f"echo {sudo_pass} | sudo -S -u postgres psql -d {db_name} -c 'GRANT CONNECT ON DATABASE {db_name} TO {user_name};'",
            f"echo {sudo_pass} | sudo -S -u postgres psql -d {db_name} -c 'GRANT USAGE ON SCHEMA public TO {user_name};'",
            f"echo {sudo_pass} | sudo -S -u postgres psql -d {db_name} -c 'GRANT SELECT ON ALL TABLES IN SCHEMA public TO {user_name};'",
            ]
        
        self._do_commands(User, commands)
        
    def ban_all_for_pg(self, User, ip_to_open='', pg_version=14):
        sudo_pass = User.password
        
        commands = [
        f'echo {sudo_pass} | sudo -S chmod 777 /etc/postgresql/{pg_version}/main/pg_hba.conf',
        f'echo {sudo_pass} | sudo -S sh -c -e "echo  ' + ' host all all all reject' + ' " >> /etc/postgresql/14/main/pg_hba.conf'
        f'echo {sudo_pass} | sudo -S sh -c -e "echo  ' + f'host \t all \t all \t {ip_to_open} \t md5 ' + ' " >> /etc/postgresql/14/main/pg_hba.conf'
        f'echo {sudo_pass} | sudo -S service postgresql restart'
        ]
        
        self._do_commands(User, commands)
        pass
        
    def install_nginx(self, User):
        sudo_pass = User.password
        commands = [
            f"echo {sudo_pass} | sudo -S apt-get update",
            f"echo {sudo_pass} | sudo -S  apt-get install nginx -y"
            ]

        
        self._do_commands(User, commands)
        
    def set_renue_nginx(self, User, ip_to_ban):
        sudo_pass = User.password

        commands = [
            f'echo {sudo_pass} | sudo -S chmod a+rx /etc/nginx/sites-available/default',
            f"""echo {sudo_pass} | """ + """sudo -S sh -c "printf 'server {deny """ + ip_to_ban + """ ; allow all; listen 80; listen [::]:80; server_name """ + self.host + """ ; return 301 http://renue.ru$request_uri;}' > /etc/nginx/sites-available/default" """,
            f"echo {sudo_pass} | sudo -S  nginx -t",
            f"echo {sudo_pass} | sudo -S  systemctl restart nginx"
            ]

        
        self._do_commands(User, commands)
        


        
