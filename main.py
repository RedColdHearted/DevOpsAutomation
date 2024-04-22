import os

from Automation import Server, User
from dotenv import load_dotenv, dotenv_values

def main():
    #загружаем все значения из .env для админа
    load_dotenv()
    name = os.getenv("SERVERS_SUPER_USER_NAME")
    password = os.getenv("SERVERS_SUPER_USER_PASSWORD")
    
    #создаем админа который является супер пользователем на серверах при необходимости можно создат ещё
    admin = User(name, password)

    #загружаем ip и порты серверов из .env
    ip1 = os.getenv("FIRST_SERVER_IP")
    port1 = os.getenv("FIST_SERVER_PORT")

    ip2 = os.getenv("SECOND_SERVER_IP")
    port2 = os.getenv("SECOND_SERVER_PORT")
    
    #создаем экземпляры сервров
    server1 = Server(ip1, port1)
    server2 = Server(ip2, port2)
    
    #выключаем авторизацию SSH по паролю
    server1.disable_ssh_password(admin)
    #создаем девопса с провами sudo
    server1.create_user_as_sudo(admin, 'DevOps')
    
    #устанавливаем postgres
    server1.install_postgresql(admin)
    
    #создаем бд
    server1.create_pg_db(admin, 'app')
    server1.create_pg_db(admin, 'custom')
    
    #создаем пользователей: имя, пароль, БД
    server1.create_pg_user(admin, 'app', 'app', 'app')
    server1.create_pg_user(admin, 'custom', 'custom', 'custom')
    
    server1.create_pg_user(admin, 'service', 'service', 'app')
    server1.create_pg_user(admin, 'service', 'service', 'custom')

    #выдаем полный конроль над БД
    server1.pg_user_give_prvg(admin, 'app', 'app')
    server1.pg_user_give_prvg(admin, 'custom', 'custom')
    
    #выдаем пользователю права на чтение БД
    server1.pg_user_for_read(admin, 'service', 'app')
    server1.pg_user_for_read(admin, 'service', 'custom')
    
    #закрываем доступ к postgres от всех ip кроме второго сервера
    server1.ban_all_for_pg(admin, ip_to_open=server2.host)
    
    
    server2.disable_ssh_password(admin)
    server2.create_user_as_sudo(admin, 'DevOps')
    server2.install_postgresql(admin)
    
    #устанавливаем nginx
    server2.install_nginx(admin)
    
    #конфигурируем nginx
    server2.set_renue_nginx(admin, server1.host)
    

if __name__ == '__main__':
    main()