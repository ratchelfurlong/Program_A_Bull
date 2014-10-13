#!usr/bin/python
import subprocess, time, threading, errno

def checkAns(test_ans, real_ans):

	if(len(test_ans) != len(real_ans)):
		return 'not equal'
	else:
		for x in range(len(real_ans)):
			if test_ans[x] == '\r':
				if '\n' != real_ans[x] or '\r' != real_ans[x]:
					return 'not equal'
			else:
				if test_ans[x] != real_ans[x]:
					return 'not equal'
		return 'equal'


def timeout( p ):
        if p.poll() is None:
            try:
            	p.kill()
            	print 'Error: process taking too long to complete--terminating'
            except OSError as e:
                if e.errno != errno.ESRCH:
                    raise


if __name__ == '__main__':
	my_input = open('test_cases.txt', 'r', 0)
	my_output = open('output.txt', 'w+')
	my_test_ans = open('output2.txt', 'r')
	k='test_cases.txt'

	p = subprocess.Popen(
		['python', 'compile_python.py'],
		stdin=my_input, 
		stdout=my_output)
	t = threading.Timer( 10.0, timeout, [p] )
	t.start()
	#p.join()
	p.wait()
	t.cancel()
	my_output.flush()
	my_output.seek(0,0)

	print checkAns(my_output.read(), my_test_ans.read())
	my_output.close()