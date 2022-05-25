import os
import copy

class ExplicitRel:
    def __init__(self) -> None:
        self.raw_text = ""
        self.raw_relations = []
        pass

def read_pdtb(tree_dir, raw_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for pdtb_dir in os.listdir(tree_dir):
        cur_dir = os.path.join(tree_dir, pdtb_dir)

        pdtb_output_dir = os.path.join(output_dir, pdtb_dir)
        if not os.path.exists(pdtb_output_dir):
            os.mkdir(pdtb_output_dir)

        if os.path.isdir(cur_dir):
            for file_name in os.listdir(cur_dir):
                if (file_name[-4:]) == "pdtb":
                    file_path = os.path.join(cur_dir, file_name)
                    raw_path =  os.path.join(raw_dir, pdtb_dir)
                    raw_path = os.path.join(raw_path, file_name[:-5]) 

                    if os.path.isfile(file_path) and os.path.isfile(raw_path):
                        print(file_path, raw_path)

                        raw_text = load_raw_text(raw_path)
                        raw_relations = load_pdtb_relation(file_path)
                        pdtb_relations = parsing_relation(raw_text, raw_relations)

                        if len(pdtb_relations) > 0:
                            pdtb_output_path = os.path.join(pdtb_output_dir, file_name[:-5] + ".rel")
                            save_pdtb(pdtb_output_path, pdtb_relations)

    return

def save_pdtb(output_path, pdtb_relations):
    with open(output_path, mode='w', encoding='utf8') as outf:
        for rel in pdtb_relations:
            sent, sent_label = rel
            sent_len = len(sent)
            for idx in range(sent_len):
                index = str(idx + 1)
                word = sent[idx]
                label = sent_label[idx] 
                conll_line = "\t".join([index, word, label]) 
                outf.write(conll_line + '\n')
            outf.write('\n')
    return

def parsing_relation(raw_text, raw_relations):
    relations = []
    for info in raw_relations:

        assert len(info) > 3
        if info[1] == '____Explicit____':
            chs, ch_labels = initial_doc(raw_text)
            conn_words, start_end_conn = parsing_conn(info[2], raw_text)
            labeling_context(ch_labels, start_end_conn, '-conn')
            conn_text = " ".join(conn_words)
            assert conn_text == info[5]

            arg1_index, start_end_args1 = find(info, '____Arg1____')
            arg1_words = parsing_args(start_end_args1, raw_text)

            arg2_index, start_end_args2 = find(info, '____Arg2____')
            arg2_words = parsing_args(start_end_args2, raw_text)

            labeling_context(ch_labels, start_end_args1, '-Arg1')
            labeling_context(ch_labels, start_end_args2, '-Arg2')

            ch_sents, ch_sent_labels = ch2sent(chs, ch_labels)

            doc, doc_labels = [], []
            for sent, sent_label in zip(ch_sents, ch_sent_labels):
                ch_words, ch_word_labels = ch2word(sent, sent_label)
                words, labels = ch_join(ch_words, ch_word_labels)
                doc.append(words)
                doc_labels.append(labels)

            conn_index = 0
            arg1_index = 0

            flag = False
            for index, (sent, sent_label) in enumerate(zip(doc, doc_labels)):
                if len(sent) == 0: continue
                label_set = set(sent_label)

                if 'B-conn' in label_set:
                    if 'B-Arg2' in sent_label: flag = True
                    conn_index = index

                if 'B-Arg1' in label_set:
                    arg1_index = index
            
            pdtb_sent = []
            pdtb_label = []

            if flag:

                for idx in range(arg1_index, conn_index + 1):
                    sent = doc[idx]
                    sent_label = doc_labels[idx]
                    pdtb_sent += sent
                    pdtb_label += sent_label
                relations.append((pdtb_sent, pdtb_label))
            

    return relations


def ch_join(ch_words, ch_word_labels):
    new_ch_words = []
    new_ch_word_labels = []

    for chs, ch_labels in zip(ch_words, ch_word_labels):
        w_list, l_list = split_word(chs, ch_labels)

        if len(w_list) > 1: 
            pass

        new_ch_words += w_list
        new_ch_word_labels += l_list

    words, labels = [], []
    for chs, ch_labels in zip(new_ch_words, new_ch_word_labels): 
        l_list = list(set(ch_labels))
        if len(l_list) > 1: assert len(l_list) == 2
        
        word = "".join(chs)
        if len(l_list) == 1:
            label = l_list[0]
        elif len(l_list) == 2: 
            label = 'B' + l_list[0][1:]
    
        words.append(word)
        labels.append(label)

    assert len(words) == len(labels) 
    check_labels(labels)
    return words, labels


def check_labels(labels):
    max_length = len(labels)

    for idx in range(max_length):
        if idx > 0:
            pre_label = labels[idx - 1]
            cur_label = labels[idx]
        else:
            continue
        if pre_label != cur_label:
            assert not (pre_label[0] == 'o' and cur_label[0] == 'I')




def split_word(chs, labels):
    max_length = len(labels)
    assert len(chs) == max_length

    temp_w = []
    temp_l = []

    pre_l = labels[0]

    w_list = []
    l_list = []

    for idx in range(max_length):

        ch = chs[idx]
        l  = labels[idx]
            
        if idx == 0:
            temp_w.append(ch)
            temp_l.append(l)
        else: 
            if not (l == pre_l or (l[0] == 'I' and pre_l[0] == 'B')):
                w_list.append(temp_w)
                l_list.append(temp_l)
                temp_w = []
                temp_l = []
            temp_w.append(ch)
            temp_l.append(l)

        pre_l = l

    if len(temp_w) > 0:
        w_list.append(temp_w)
        l_list.append(temp_l)

    return w_list, l_list
            
def ch2word(chs, ch_labels):
    sents = []
    sent_labels = []

    ch_length = len(chs) 
    words = []
    labels = []
    for idx in range(ch_length):
        ch = chs[idx] 
        label = ch_labels[idx] 
        if ch == ' ':
            if len(words) == 0: continue
            sents.append(words)
            sent_labels.append(labels)
            words = []
            labels = []
        else:
            words.append(ch)
            labels.append(label)
    
    if len(words) > 0:
        sents.append(words)
        sent_labels.append(labels)
    return sents, sent_labels



def ch2sent(chs, ch_labels):
    sents = []
    sent_labels = []

    ch_length = len(chs) 
    words = []
    labels = []
    for idx in range(ch_length):
        ch = chs[idx] 
        label = ch_labels[idx] 
        if ch == '\n':
            sents.append(copy.deepcopy(words))
            sent_labels.append(copy.deepcopy(labels))
            words = []
            labels = []
        else:
            words.append(ch)
            labels.append(label)
    return sents, sent_labels


def initial_doc(raw_text):
    chs = []
    labels = []
    for i in raw_text:
        chs.append(i)
        labels.append('o')
    return chs, labels

def labeling_context(labels, start_end_args, context):
    for (start, end) in start_end_args:
        for idx, index in enumerate(range(start, end)):
            if idx == 0:
                labels[index] = 'B' + context
            else:
                labels[index] = 'I' + context

def parsing_conn(conn_index, raw_text):
    info = conn_index.split(";")
    conn_words = []
    start_end_conn = []
    for start_end_index in info:
        start, end = start_end_index.split("..")
        conn_words.append(raw_text[ int(start): int(end) ])
        start_end_conn.append((int(start), int(end)))
    return conn_words, start_end_conn

def find(info, context):
    for idx, line in enumerate(info):
        #if line == '____Arg1____':
        if line == context:
            info_index = info[idx + 1].split(";")
            start_end_index = []
            for index_split in info_index:
                start, end = index_split.split("..")
                start_end_index.append((int(start), int(end)))
            return idx, start_end_index

def parsing_args(arg1_index, raw_text):
    arg1_words = []
    for (start, end) in arg1_index:
        arg1_words.append(raw_text[ int(start): int(end) ])
    return arg1_words

def load_pdtb_relation(path):
    with open(path, encoding='utf8', mode='r') as inf:
        info_list = []
        for info in readInfo(inf.readlines()):
            info_list.append(info)
    return info_list

def load_raw_text(path):
    with open(path, mode='r') as inf:
        text = ""
        for line in inf.readlines():
            text += line
        return text

def readInfo(file):
    info = []
    for line in file:
        tok = line.rstrip()
        if tok == "________________________________________________________" and len(info) > 0:
            yield info
            info = []
        else:
            info.append(tok)
    if len(info) != 0:
        yield info

if __name__ == '__main__':
    read_pdtb("pdtb_data/pdtb_relations", "pdtb_data/raw/wsj", 'output_debug')