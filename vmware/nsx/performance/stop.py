from paramiko import SSHClient, AutoAddPolicy

def main():

	tenant1 = SSHClient()
	tenant2 = SSHClient()
	i = 2
	while True:
		tenant1.set_missing_host_key_policy(AutoAddPolicy())
		tenant1.connect('1.1.1.%s' % str(i), username='tenant', password='tenant')
		
		stdin, stdout, stderr = tenant1.exec_command("killall nuttcp", get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		tenant2.set_missing_host_key_policy(AutoAddPolicy())
		tenant2.connect('1.1.1.%s' % str((i+1)), username='tenant', password='tenant')
			
		stdin, stdout, stderr = tenant2.exec_command("killall nuttcp", get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		i += 2
		if i == 122:
			break

if __name__ == '__main__':
	exit(main())