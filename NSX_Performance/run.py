from paramiko import SSHClient, AutoAddPolicy

def main():

	N = 7
	
	tenant1 = SSHClient()
	tenant2 = SSHClient()

	for i in range(7,N+3):

		tenant1.set_missing_host_key_policy(AutoAddPolicy())
		tenant1.connect('200.0.0.%s' % i, username='tenant', password='tenant')
		stdin, stdout, stderr = tenant1.exec_command("sudo sed -i -e 's/hosthost/host%s/g' /etc/collectd/collectd.conf" % i, get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		stdin, stdout, stderr = tenant1.exec_command("sudo service collectd restart", get_pty=True)
		stdin, stdout, stderr = tenant1.exec_command("sudo route del default gw 200.0.0.1")
		stdin, stdout, stderr = tenant1.exec_command("sudo route add default gw 192.168.0.1")

		tenant2.set_missing_host_key_policy(AutoAddPolicy())
		tenant2.connect('200.0.0.%s' % (i+1), username='tenant', password='tenant')
		stdin, stdout, stderr = tenant2.exec_command("sudo sed -i -e 's/hosthost/host%s/g' /etc/collectd/collectd.conf" % (i+1), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		stdin, stdout, stderr = tenant2.exec_command("sudo service collectd restart", get_pty=True)
		stdin, stdout, stderr = tenant2.exec_command("sudo route del default gw 200.0.0.1")
		stdin, stdout, stderr = tenant2.exec_command("sudo route add default gw 192.168.1.1")

		stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 6666")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 6666")

		stdin, stdout, stderr = tenant1.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -Ru -ws 8m -M 1500 -T 20 192.168.1.2")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -Ru -ws 8m -M 1500 -T 20 192.168.0.2")
		

		i += 1

if __name__ == '__main__':
	exit(main())