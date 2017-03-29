from paramiko import SSHClient, AutoAddPolicy


def main():
	
	client = SSHClient()
	server = SSHClient()

	client.set_missing_host_key_policy(AutoAddPolicy())
	client.connect('200.0.0.2', username='tenant', password='tenant')
	stdin, stdout, stderr = client.exec_command("sed -i -e 's/Hostname 'collectd'/Hostname 'collectd1'/g' /etc/collectd/collectd.conf")

	server.set_missing_host_key_policy(AutoAddPolicy())
	server.connect('200.0.0.3', username='tenant', password='tenant')
	stdin, stdout, stderr = server.exec_command("sed -i -e 's/Hostname 'collectd'/Hostname 'collectd2'/g' /etc/collectd/collectd.conf")

if __name__ == '__main__':
	exit(main())