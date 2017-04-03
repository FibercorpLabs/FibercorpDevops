from paramiko import SSHClient, AutoAddPolicy

def main():

	N = 7
	
	client = SSHClient()
	server = SSHClient()

	for i in range(7,N+3):

		client.set_missing_host_key_policy(AutoAddPolicy())
		client.connect('200.0.0.%s' % i, username='tenant', password='tenant')
		stdin, stdout, stderr = client.exec_command("sudo sed -i -e 's/hosthost/host%s/g' /etc/collectd/collectd.conf" % i, get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		stdin, stdout, stderr = client.exec_command("sudo service collectd restart", get_pty=True)
		stdin, stdout, stderr = client.exec_command("nuttcp -S -p 6666", get_pty=True)

		server.set_missing_host_key_policy(AutoAddPolicy())
		server.connect('200.0.0.%s' % (i+1), username='tenant', password='tenant')
		stdin, stdout, stderr = server.exec_command("sudo sed -i -e 's/hosthost/host%s/g' /etc/collectd/collectd.conf" % (i+1), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		stdin, stdout, stderr = server.exec_command("sudo service collectd restart", get_pty=True)
		stdin, stdout, stderr = server.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -Ru -ws 8m -M 1500 -T 7200 200.0.0.%s" % i , get_pty=True)

		i += 1

if __name__ == '__main__':
	exit(main())