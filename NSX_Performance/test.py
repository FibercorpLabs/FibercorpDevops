from paramiko import SSHClient, AutoAddPolicy

def main():

	
		tenant1 = SSHClient()
		tenant1.set_missing_host_key_policy(AutoAddPolicy())
		tenant1.connect('1.1.1.2', username='tenant', password='tenant')
		stdin, stdout, stderr = tenant1.exec_command("sudo sed -i -e 's/hosthost/host2/g' /etc/collectd/collectd.conf", get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()		

		stdin, stdout, stderr = tenant1.exec_command("sudo sed -i -e 's/200.0.0.252/1.1.1.252/g' /etc/collectd/collectd.conf", get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		print "Done"

if __name__ == '__main__':
	exit(main())