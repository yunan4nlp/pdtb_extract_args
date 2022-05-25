import os 

if __name__ == '__main__':
	input_dir = 'output_debug_conll'

	for sec in os.listdir(input_dir):
		pdtb_path = os.path.join(input_dir, sec)
		if os.path.isdir(pdtb_path):
			for file in os.listdir(pdtb_path):
				cmd = 'cat ' + pdtb_path + "/*.rel.tok > " + input_dir + '/' + sec + ".rel.tok"
			print(cmd)
			os.system(cmd)
