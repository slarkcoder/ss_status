import paramiko, json, os
import multiprocessing

#读取服务器列表
def get_server_list():
    with open('server.json', 'r', encoding='utf_8') as file:
        server = json.load(file)
        return server["server"]

#检查 Shadowsocks 服务状态
def check_shadowsocks_status(server,ssh):
    print(server, ": shadowsocks status")
    stdin, stdout, stderr = ssh.exec_command("/etc/init.d/shadowsocks status")
    for str in stdout.readlines():
        print(str)
        if "ShadowsocksR is stopped" in str:
            restart_shadowsocks(server, ssh)

#重启 Shadowsocks 服务
def restart_shadowsocks(server, ssh):
    stdin, stdout, stderr = ssh.exec_command("/etc/init.d/shadowsocks restart")
    print(server, ": shadowsocks restart complete")

#重启锐速
def restart_server_speeder(server, ssh):
    stdin, stdout, stderr = ssh.exec_command("/serverspeeder/bin/serverSpeeder.sh restart")
    for str in stdout.readlines():
        print(str)
    print(server, ": serverspeeder restart complete")

#建立服务器 SSHClient
def connect_server(server):
    print("current pid :",os.getpid())

    hostname = server["hostname"]
    port = server["port"]
    username = server["username"]
    password = server["password"]
    name = server["name"]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, port=port, username=username, password=password)
    check_shadowsocks_status(name, ssh)
    ssh.close()

if __name__=='__main__':
    servers = get_server_list()
    pool = multiprocessing.Pool()
    cpus = multiprocessing.cpu_count()

    for server in servers:
        pool.apply_async(connect_server(server))

    print('Waiting for all subprocesses done...')
    pool.close()
    pool.join()
    print('All subprocesses done.')
