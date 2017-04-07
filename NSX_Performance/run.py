from paramiko import SSHClient, AutoAddPolicy
from time import sleep

def main():

	tenant1 = SSHClient()
	tenant2 = SSHClient()
	i = 2
	while True:
		tenant1.set_missing_host_key_policy(AutoAddPolicy())
		tenant1.connect('1.1.1.%s' % str(i), username='tenant', password='tenant')
		
		#stdin, stdout, stderr = tenant1.exec_command("sudo service collectd restart", get_pty=True)
		#stdin.write('tenant\n')
		#stdin.flush()

		#print "Restarted: %s" % str(i)
		
		tenant2.set_missing_host_key_policy(AutoAddPolicy())
		tenant2.connect('1.1.1.%s' % str((i+1)), username='tenant', password='tenant')
			
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 6666")
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 6667")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 6666")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 6667")

		stdin, stdout, stderr = tenant1.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -R10 -ws 8m -M 1500 -T 1800 192.168.1.2")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -R10 -ws 8m -M 1500 -T 1800 192.168.0.2")
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -u -b -v -I ens192 -l8192 -N 1 -p 6667 -R10 -ws 8m -T 1800 192.168.1.2")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -u -b -v -I ens192 -l8192 -N 1 -p 6667 -R10 -ws 8m -T 1800 192.168.0.2")
		
		print "Test %s is running" % str(i)
		print "Test %s is running" % str(i+1)

		sleep(0.5)

		i += 2
		if i == 122:
			break

if __name__ == '__main__':
	exit(main())