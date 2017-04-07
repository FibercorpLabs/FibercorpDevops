from paramiko import SSHClient, AutoAddPolicy
from time import sleep

def main():

	tenant1 = SSHClient()
	tenant2 = SSHClient()
	i = 2

	while True:

		tenant1.set_missing_host_key_policy(AutoAddPolicy())
		tenant1.connect('1.1.1.%s' % str(i), username='tenant', password='tenant')
		
		tenant2.set_missing_host_key_policy(AutoAddPolicy())
		tenant2.connect('1.1.1.%s' % str((i+1)), username='tenant', password='tenant')
			
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 10000")		
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 20000")
		
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 10000")		
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 20000")
		
		# Starting UDP Traffic
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -b -v -I ens192 -l8192 \
		 -N 1 -p 10000 -R10 -ws 8m -M 1500 -T 1800 192.168.1.2")
		stdin, stdout, stderr = tenant1.exec_command("nuttcp -u -b -v -I ens192 -l8192 \
		 -N 1 -p 20000 -R10 -ws 8m -T 1800 192.168.1.2")

		# Starting TCP Traffic		
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -b -v -I ens192 -l8192 \
		 -N 1 -p 10000 -R10 -ws 8m -M 1500 -T 1800 192.168.0.2")
		stdin, stdout, stderr = tenant2.exec_command("nuttcp -u -b -v -I ens192 -l8192 \
		 -N 1 -p 20000 -R10 -ws 8m -T 1800 192.168.0.2")
				
		print "Test %s is running." % str(i/2)

		i += 2
		if i == 4:
			break

if __name__ == '__main__':
	exit(main())