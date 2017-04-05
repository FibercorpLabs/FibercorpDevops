from paramiko import SSHClient, AutoAddPolicy

def main():

	tenant1 = SSHClient()
	tenant2 = SSHClient()
	i = 1
	while True:
		tenant1.set_missing_host_key_policy(AutoAddPolicy())
		tenant1.connect('1.1.1.%s' % str(i), username='tenant', password='tenant')
		
		

		stdin, stdout, stderr = tenant1.exec_command("sudo sed -i -e 's/hosthost/host%s/g' /etc/collectd/collectd.conf" % str(i), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()
		stdin, stdout, stderr = tenant1.exec_command("sudo sed -i -e 's/1.1.1.252%s/1.1.1.252/g' /etc/collectd/collectd.conf" % str(i), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()
		stdin, stdout, stderr = tenant1.exec_command("sudo sed -i -e 's/1.1.1.252%s/1.1.1.252/g' /etc/collectd/collectd.conf" % str(i-1), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		stdin, stdout, stderr = tenant1.exec_command("sudo service collectd restart", get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		print "Connected: %s" % str(i)
		
		#stdin, stdout, stderr = tenant1.exec_command("sudo route del default gw 1.1.1.1", get_pty=True)
		#stdin.write('tenant\n')
		#stdin.flush() 
		#stdin, stdout, stderr = tenant1.exec_command("sudo route add default gw 192.168.0.1", get_pty=True)
		#stdin.write('tenant\n')
		#stdin.flush()

		tenant2.set_missing_host_key_policy(AutoAddPolicy())
		tenant2.connect('1.1.1.%s' % str((i+1)), username='tenant', password='tenant')
			
		stdin, stdout, stderr = tenant2.exec_command("sudo sed -i -e 's/hosthost/host%s/g' /etc/collectd/collectd.conf" % str(i+1), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()
		stdin, stdout, stderr = tenant2.exec_command("sudo sed -i -e 's/1.1.1.252%s/1.1.1.252/g' /etc/collectd/collectd.conf" % str(i), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()
		stdin, stdout, stderr = tenant2.exec_command("sudo sed -i -e 's/1.1.1.252%s/1.1.1.252/g' /etc/collectd/collectd.conf" % str(i-1), get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()


		stdin, stdout, stderr = tenant2.exec_command("sudo service collectd restart", get_pty=True)
		stdin.write('tenant\n')
		stdin.flush()

		print "Connected: %s" % str(i+1)
		#stdin, stdout, stderr = tenant2.exec_command("sudo route del default gw 1.1.1.1", get_pty=True)
		#stdin.write('tenant\n')
		#stdin.flush()
		#stdin, stdout, stderr = tenant2.exec_command("sudo route add default gw 192.168.1.1", get_pty=True)
		#stdin.write('tenant\n')
		#stdin.flush()

		#stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 6666")
		#stdin, stdout, stderr = tenant1.exec_command("nuttcp -S -p 6667")
		#stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 6666")
		#stdin, stdout, stderr = tenant2.exec_command("nuttcp -S -p 6667")

		#stdin, stdout, stderr = tenant1.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -Ru -ws 8m -M 1500 -T 3600 192.168.1.2")
		#stdin, stdout, stderr = tenant2.exec_command("nuttcp -b -v -I ens192 -l8192 -N 1 -p 6666 -Ru -ws 8m -M 1500 -T 3600 192.168.0.2")
		#stdin, stdout, stderr = tenant1.exec_command("nuttcp -u -b -v -I ens192 -l8192 -N 1 -p 6667 -Ru -ws 8m -T 3600 192.168.1.2")
		#stdin, stdout, stderr = tenant2.exec_command("nuttcp -u -b -v -I ens192 -l8192 -N 1 -p 6667 -Ru -ws 8m -T 3600 192.168.0.2")
		

		i += 1
		if i == 122:
			break

if __name__ == '__main__':
	exit(main())