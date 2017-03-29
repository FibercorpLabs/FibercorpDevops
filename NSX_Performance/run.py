from paramiko import SSHClient, AutoAddPolicy


def main():
	
	client = SSHClient()
	server = SSHClient()

	client.set_missing_host_key_policy(AutoAddPolicy())
	client.connect('200.0.0.2', username='tenant', password='tenant')
	stdin, stdout, stderr = client.exec_command("sudo sed -i -e 's/hosthost/host1/g' /etc/collectd/collectd.conf")
	stdin.write('tenant\n')
	stdin.flush()

	server.set_missing_host_key_policy(AutoAddPolicy())
	server.connect('200.0.0.3', username='tenant', password='tenant')
	stdin, stdout, stderr = server.exec_command("sudo sed -i -e 's/hosthost/host2/g' /etc/collectd/collectd.conf")
	stdin.write('tenant\n')
	stdin.flush()
if __name__ == '__main__':
	exit(main())