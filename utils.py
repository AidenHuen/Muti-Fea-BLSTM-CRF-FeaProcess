# encoding:utf-8
import codecs
import math
import pickle
import random
path_eng_name = "./data/English_Cn_Name_Corpus（48W）.txt"  # 国外移民语聊
path_cn_name = "./data/Chinese_Names_Corpus（120W）.txt"  # 中文人名语料
train_path = "./data/trainset_1.txt" # 未添加特征的训练集路径
test_path = "./data/testset_answer_1.txt" # 未添加特征的测试集路径
kb = 2  # 边界特征切割值k
ku = 5  # 用字特征切割值k
test_output = "data/testset_answer_10" # 添加特征后的测试集输出路径
train_output = "data/trainset_10" # 添加特征后的测试集输出路径

border_corpus = "./word2vec/data/train_text/film_train.txt"  # 边界特征训练语聊

def read_name_corpus():
    """
    读取中英文语聊
    :return:
    """
    f = codecs.open(path_cn_name, encoding="utf-8")
    data = f.read()
    f.close()
    cn_name = data.split("\r\n")

    f = codecs.open(path_eng_name, encoding="utf-8")
    data = f.read()
    f.close()
    eng_name = data.split("\r\n")
    return cn_name, eng_name

def get_char_dict_list():
    cn_name, eng_name = read_name_corpus()
    char_dict_list = [{}, {}, {}, {}, {}, {}, {}]
    for name in cn_name:
        if name.__len__() == 2:
            try:
                char_dict_list[0][name[0]] += 1.0
            except:
                char_dict_list[0][name[0]] = 1.0
            try:
                char_dict_list[1][name[1]] += 1.0
            except:
                char_dict_list[1][name[1]] = 1.0
        if name.__len__() == 3:
            try:
                char_dict_list[0][name[0]] += 1.0
            except:
                char_dict_list[0][name[0]] = 1.0
            try:
                char_dict_list[2][name[1]] += 1.0
            except:
                char_dict_list[2][name[1]] = 1.0
            try:
                char_dict_list[3][name[2]] += 1.0
            except:
                char_dict_list[3][name[2]] = 1.0

    for name in eng_name:

        try:
            char_dict_list[4][name[0]] += 1.0
        except:
            char_dict_list[4][name[0]] = 1.0

        try:
            char_dict_list[6][name[name.__len__() - 1]] += 1.0
        except:
            char_dict_list[6][name[name.__len__() - 1]] = 1.0

        if name.__len__() >= 3:
            for i in range(1, name.__len__() - 1):
                try:
                    char_dict_list[5][name[i]] += 1.0
                except:
                    char_dict_list[5][name[i]] = 1.0

    for dict in char_dict_list:
        max_value = max(list(dict.values()))
        min_value = min(list(dict.values()))
        for word in dict:
            dict[word] = int(round(math.log(dict[word] - min_value + 1) / math.log(max_value - min_value + 1) *ku))
            # dict[word] = 1
            # dict[word] = int(round((dict[word] - min_value + 1) / (max_value - min_value + 1) * k))
    # for word in char_dict_list[0].keys():
    #     print word
    #     print(char_dict_list[0][word])
    return char_dict_list

def get_border_corpus():
    f = codecs.open(border_corpus, encoding="utf-8")
    rows = f.readlines()
    f.close()
    comment_corpus = [row.strip().replace(" ", "") for row in rows]
    random.shuffle(comment_corpus)
    return comment_corpus

def get_trainset_name():
    f = codecs.open(train_path, encoding="utf-8")
    data = f.read()
    f.close()
    data = data.split("\n")
    items = [row.split("\t")for row in data]
    names = []
    for i, item in enumerate(items):
        if item.__len__()>1 and item[1][0] == "B":
            name = item[0]
            begin = i+1
            for j in range(begin, items.__len__()):
                if items[j][1][0] == "E":
                    name += items[j][0]
                    names.append(name)
                    break
                else:
                    name += items[j][0]

    names = list(set(names))
    return names

def save_border_dict_list_pk():
    comments = get_border_corpus()
    names = get_trainset_name()
    boder_dict_list = [{}, {}]
    comments = comments[:1000000]
    for comment in comments:
        for name in names:
            try:
                index = comment.index(name)
                if index-1 >= 0:
                    try:
                        boder_dict_list[0][comment[index-1]] += 1.0
                    except:
                        boder_dict_list[0][comment[index-1]] = 1.0
                end = index+name.__len__()
                if end < comment.__len__():
                    try:
                        boder_dict_list[1][comment[end]] += 1.0
                    except:
                        boder_dict_list[1][comment[index-1]] = 1.0
            except:
                continue
    char_freq = {}
    chars = list(set(list(boder_dict_list[0].keys())+list(boder_dict_list[1].keys())))
    for comment in comments:
        for char in chars:
            num = comment.count(char)
            try:
                char_freq[char] += num
            except:
                char_freq[char] = num

    for char in chars:
        if boder_dict_list[0].has_key(char):
            boder_dict_list[0][char] = (boder_dict_list[0][char]+1.0)/math.log(char_freq[char]+1.0)
        if boder_dict_list[1].has_key(char):
            boder_dict_list[1][char] = (boder_dict_list[1][char] + 1.0)/math.log(char_freq[char] + 1.0)
    for word in boder_dict_list[1]:
        print word, boder_dict_list[1][word]

    pickle.dump(boder_dict_list, open("./data/border_dict_list","wb"))

def get_border_dict_list():
    border_dict_list = pickle.load(open("./data/border_dict_list", "rb"))
    for dict in border_dict_list:
        for word in dict:
            dict[word] = math.log(dict[word]+1, 2)
        max_c = max(dict.values())
        min_c = min(dict.values())
        for word in dict:
            dict[word] = int(round(((dict[word]-min_c)/(max_c-min_c))*kb))
            print word, dict[word]

    for dict in border_dict_list:
        for word in dict:
            print word, dict[word]
    return border_dict_list

def add_feture(dict_list,input,output):
    f = codecs.open(input, encoding="utf-8")
    rows = f.read().split("\n")
    new_rows = []
    for row in rows:
        items = row.split("	")
        if items.__len__() == 1:
            new_rows.append(items[0])
        else:
            features = []
            for char_dict in dict_list:
                try:
                    features.append(str(char_dict[items[0]]))
                except:
                    features.append("0")
            row = items[0]+"	"+ "	".join(features)+"	"+items[1]
            new_rows.append(row)
    data = "\n".join(new_rows)
    f = codecs.open(output,"w", encoding="utf-8")
    f.write(data)
    f.close()


if __name__ == "__main__":
    # dict_list = get_char_dict_list()
    # add_feture(dict_list, test_path, test_output)
    # add_feture(dict_list, train_path, train_output)
    # save_border_dict_list_pk()
    border_list = get_border_dict_list()
    char_list = get_char_dict_list()
    dict_list = char_list+border_list
    # # print(len(dict_list))
    add_feture(dict_list, train_path, train_output)
    add_feture(dict_list, test_path, test_output)