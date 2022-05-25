import os
from nltk.tokenize import word_tokenize
from numpy import outer

def read_raw(input_dir, output_dir):

	if not os.path.exists(output_dir): os.mkdir(output_dir)


	for pdtb_dir in os.listdir(input_dir):
		pdtb_path = os.path.join(input_dir, pdtb_dir)
		pdtb_output_path = os.path.join(output_dir, pdtb_dir)
		if not os.path.exists(pdtb_output_path): os.mkdir(pdtb_output_path)

		if os.path.isdir(pdtb_path):
			for file in os.listdir(pdtb_path):
				if file[-3:] == 'rel':
					print(file)
					rel_file = os.path.join(pdtb_path, file)
					conll_tokens_rels, conll_labels_rels = raw2token(rel_file)
					rel_output_file = os.path.join(pdtb_output_path, file + '.tok')
					save_conll(rel_output_file, conll_tokens_rels, conll_labels_rels)

	return

def save_conll(output_file, conll_tokens_rels, conll_labels_rels):
	with open(output_file, mode='w', encoding='utf8') as inf:
		for conll_tokens, conll_labels in zip(conll_tokens_rels, conll_labels_rels):
			for idx, (token, label) in enumerate(zip(conll_tokens, conll_labels)):
				info = [str(idx + 1), token, label]
				inf.write('\t'.join(info) + '\n')
			inf.write('\n')
			pass
	return

def raw2token(rel_path):
	with open(rel_path, mode='r', encoding='utf')  as inf:

		conll_tokens_rels = []
		conll_labels_rels  = []

		for sents in read_conll(inf.readlines()):
			conll_tokens = []
			conll_labels = []

			for line in sents:
				index, word, label = line.strip().split("\t")
				tokens = word_tokenize(word)

				token_labels = label_tokenize(tokens, label)

				conll_tokens += tokens
				conll_labels += token_labels

			assert len(conll_tokens) == len(conll_labels)
			conll_tokens_rels.append(conll_tokens)
			conll_labels_rels.append(conll_labels)
	return conll_tokens_rels, conll_labels_rels

def label_tokenize(tokens, label):
	token_labels = []

	token_len = len(tokens)

	if token_len == 1:
		token_labels = [label]
	else:
		if label[0] == 'o' or label[0] == 'I':
			token_labels = [label] * token_len
		elif label[0] == 'B':
			token_labels = [label]
			token_labels += ['I' + label[1:]] * (token_len - 1)

	return token_labels




def read_conll(file):
    info = []
    for line in file:
        line = line.rstrip()
        if line == '':
            yield info
            info = []
        else:
            info.append(line)
    if len(info) != 0:
        yield info



if __name__ == '__main__':
	input_dir = "output_debug"
	output_dir = input_dir + "_conll"

	read_raw(input_dir, output_dir)