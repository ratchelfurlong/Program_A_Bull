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

def grade_submission()
    test_input = open(test_input_path, 'r')
    test_output = open(test_output_path, 'r')
    user_file_output = open(user_output_file_path, 'w+')

	if file_ext == 'java':
        pre = subprocess.Popen(['javac', file_path])
        pre.wait()

        p = subprocess.Popen(
            ['java', exec_name],
            stdin=test_input, 
            stdout=user_file_output
        )
    elif file_ext == 'cs':
        pre = subprocess.Popen(['mcs', file_name])
        pre.wait()

        p = subprocess.Popen(
            ['mono', exec_name+'.exe'],
            stdin=test_input, 
            stdout=user_file_output
        )
	t = threading.Timer( 10.0, timeout, [p] )
	t.start()
	#p.join()
	p.wait()
	t.cancel()
	my_output.flush()
	my_output.seek(0,0)

	print checkAns(my_output.read(), my_test_ans.read())
	my_output.close()