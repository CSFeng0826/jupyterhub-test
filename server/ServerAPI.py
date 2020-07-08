from flask import Flask, request
from nltk.metrics.distance import jaccard_distance
import pandas as pd
from Levenshtein import distance
import datetime
import json
import os
import re

def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = "Content-Type"
    return response
    
app = Flask(__name__)
app.after_request(after_request)

@app.route('/GetCode/<nid>', methods=['POST'])
def GetCode(nid):
    # POST data receive
    data = request.json

    # save path
    base_url = "D:/workspace/user/"
    if not os.path.exists(base_url + nid):
        os.makedirs(base_url + nid)
    data['code'] = data['code'].replace('\u00a0\n', '')
    # get compile time
    data["time"] = str(datetime.datetime.now())

    # write to log
    fp = open(base_url + nid + "/jupyterhub-" + str(datetime.date.today()) + ".log", "a")
    fp.writelines(json.dumps(data) + "\n")
    fp.close()
    return data

@app.route('/ErrorMsg/<nid>', methods=['POST'])
def ErrorMsg(nid):
    # POST data receive
    data = request.json

    # save path
    base_url = "D:/workspace/user/"

    # clean traceback data
    reaesc = re.compile(r'\x1b[^m]*m')
    new_text = []
    for i in data["traceback"]:
        new_text.append(reaesc.sub('', i))
    data["traceback"] = new_text

    # write to log
    fname = base_url + nid + "/jupyterhub-" + str(datetime.date.today()) + ".log"
    lines = []
    log = {}
    with open(fname, 'r') as f:
        lines = f.readlines()
        log = json.loads(lines[-1])
        for key in data:
            log[key] = data[key]
        lines[-1] = json.dumps(log) + "\n"
    with open(fname, 'w') as f:
        for line in lines:
            f.writelines(line)

    error_line_split = re.compile(r' \(<\S+-\S+-\S+-\S+>, \S+ ')
    error_pair = error_line_split.split(str(log['evalue']))
    replace = re.sub(r"\'\S+\'", "VAR", error_pair[0])
    replace = re.sub(r"\'[\S ]+\'", "VAR", replace)
    replace = re.sub(r"[0-9]+", "NUMBER", replace)
    replace = re.sub(r"can't assign to [\S ]*", "can't assign to", replace)
    try:
        temp = replace.split('.')
        error_pair[0] = temp[0]
    except:
        pass

    error_pair[0] = replace

    try:
        error_pair[1] = int(error_pair[1].replace(")", ""))
    except:
        if len(error_pair) == 1:
            error_pair.append(-1)
        else:
            error_pair[1] = -1
        pass

    print()
    print(error_pair)
    print(log['code'].split('\n')[error_pair[1]])

    keyword = []
    # error_line = []
    if error_pair[1] != -1:
        try:
            error_code = log['code'].split('\n')[error_pair[1]]
            tk = tokenlize(error_code)
            #error_line.append(error_code)
            for tk_count in range(0, len(tk)):
                if tk[tk_count][0] == 'FUNCTION' or tk[tk_count][0] == 'KEYWORD':
                    keyword.append(tk[tk_count][1])
        except:
            pass

    print(keyword)

    knowledgebase = pd.read_excel("D:/workspace/data/test_data/knowledgebase.xlsx", encoding='utf-8')

    knowledgebase = knowledgebase[knowledgebase.ename == log['ename']]
    knowledgebase = knowledgebase.reset_index(drop=True)

    guide = {'guide':'', 'link_name':[], 'link':[]}
    
    for knowledgebase_count in range(0, len(knowledgebase)):
        if distance(error_pair[0], knowledgebase.iloc[knowledgebase_count].evalue) == 0:
            if log['ename'] == 'SyntaxError' and error_pair[0] == 'invalid syntax':
                guide['guide'] = knowledgebase.iloc[knowledgebase_count].guide

                tutorial_candidate = {'difference':[], 'count':[]}
                knowledgebase_tutorial = pd.read_excel("D:/workspace/data/test_data/knowledgebase_tutorial.xlsx", encoding='utf-8')
                
                for tutorial_count in range(0, len(knowledgebase_tutorial)):
                    difference = jaccard(set(keyword), set(eval(knowledgebase_tutorial.iloc[tutorial_count].keyword)))
                    tutorial_candidate['difference'].append(difference)
                    tutorial_candidate['count'].append(tutorial_count)
                
                max_difference = max(tutorial_candidate['difference'])

                if max_difference != 0:
                    for diff_count in range(0, len(tutorial_candidate['difference'])):
                        if tutorial_candidate['difference'][diff_count] == max_difference:
                            if knowledgebase_tutorial.iloc[diff_count].link_name in guide['link_name'] and knowledgebase_tutorial.iloc[diff_count].link in guide['link']:
                                pass
                            else:
                                guide['link_name'].append(knowledgebase_tutorial.iloc[diff_count].link_name)
                                guide['link'].append(knowledgebase_tutorial.iloc[diff_count].link)
                else:
                    pass
            else:
                guide['guide'] = knowledgebase.iloc[knowledgebase_count].guide
                guide['link_name'].append(knowledgebase.iloc[knowledgebase_count].link_name)
                guide['link'].append(knowledgebase.iloc[knowledgebase_count].link)

    return guide

@app.route('/GetCourseList', methods=['GET'])
def GetCourseList():
    # POST data receive
    course_data = []
    file_list = os.listdir("D:/workspace/data/test_data/course_data/problem_grade")
    for file_count in range(0, len(file_list)):
        course = []
        df = pd.read_csv("D:/workspace/data/test_data/course_data/problem_grade/" + file_list[file_count], encoding='utf-8')
        columns = list(df.columns)
        problem_name = columns[6:]
        file_list[file_count] = file_list[file_count].replace("_grades.csv", "")
        course.append(file_list[file_count])
        for problem_count in range(0, len(problem_name)):
            problem_name[problem_count] = problem_name[problem_count].replace(" 成績", "")
        course.append(problem_name)
        course_data.append(course)
    return dict(course_data)

@app.route('/GetStudentData', methods=['POST'])
def GetStudentData():
    # POST data receive
    nid  = request.args.get('nid', None)
    assignment_name  = request.args.get('assignment', None)
    problem_name  = request.args.get('problem', None)
    if nid != None or problem_name != None:
        student_data = get_student_data(nid, assignment_name, problem_name)
        return student_data
    else:
        return {"error":"未傳入學號、作業名稱以及問題名稱"}

@app.route('/GetStudentGrade', methods=['POST'])
def GetStudentGrade():
    assignment_name  = request.args.get('assignment', None)
    if assignment_name != None:
        try:
            df = pd.read_csv("D:/workspace/data/test_data/course_data/problem_grade/" + assignment_name + "_grades.csv")
            df = df[df['姓名'].notnull()]
            df = df.reset_index(drop=True)
            data = df.values.tolist()
            columns = list(df.columns)
            return {'columns':columns, 'student_data':data}
        except:
            return {"error":"作業名稱錯誤"}
    else:
        df = pd.read_csv("D:/workspace/data/test_data/course_data/course_grade/grades.csv")
        df = df[df['姓名'].notnull()]
        df = df.reset_index(drop=True)
        data = df.values.tolist()
        columns = list(df.columns)
        return {'columns':columns, 'student_data':data}

@app.route('/GetErrorTypeMsg', methods=['POST'])
def GetErrorTypeMsg():
    # POST data receive
    nid  = request.args.get('nid', None)
    problem_name  = request.args.get('problem', None)

    if nid != None and problem_name != None:
        error_log_df = pd.read_excel("D:/workspace/data/test_data/error_log.xlsx", encoding='utf-8')
        if nid.lower() not in set(error_log_df.username.to_list()):
            return {"error":"學號輸入錯誤"}
        else:
            error_log_df = error_log_df[(error_log_df.username == nid.lower()) & (error_log_df.file_name == problem_name)]

            if len(error_log_df) == 0:
                return {}
            else:
                ename_dummies = pd.get_dummies(error_log_df['ename']).sum()
                response = {'ename':[], 'count':[]}
                for ename, count in ename_dummies.items():
                    response['ename'].append(ename)
                    response['count'].append(count)
                return response
    elif nid == None and problem_name != None:
        error_log_df = pd.read_excel("D:/workspace/data/test_data/error_log.xlsx", encoding='utf-8')
        error_log_df = error_log_df[error_log_df.file_name == problem_name]

        if len(error_log_df) == 0:
            return {}
        else:
            ename_dummies = pd.get_dummies(error_log_df['ename']).sum()
            response = {'ename':[], 'count':[]}
            for ename, count in ename_dummies.items():
                response['ename'].append(ename)
                response['count'].append(count)
            return response
    else:
        return {"error":"未傳入學號及問題名稱"}

def jaccard(a, b):
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

def get_student_data(nid, assignment_name, problem_name):
    log_df = pd.read_csv("D:/workspace/data/test_data/log.csv", encoding='utf-8')

    if nid not in set(log_df.username.to_list()):
        return {}
    else:
        student_log_df = log_df[((log_df.username == nid) & (log_df.file_name == problem_name))]
        
        student_df = pd.read_excel("D:/workspace/data/test_data/1081Python_name.xlsx", encoding='utf-8')
        student_df = student_df.drop(['grade', 'dept_detail'], axis=1)
        
        student_index = student_df[student_df.nid == nid.upper()].index
        student_dict = student_df.iloc[student_index].to_dict('index')[0]
        student_dict["exec_counts"] = len(student_log_df)
        assignment_df = pd.read_csv("D:/workspace/data/test_data/course_data/problem_grade/" + assignment_name + "_grades.csv")
        assignment_df = assignment_df[assignment_df["學號"] == nid]
        print(assignment_df)
        student_dict["problem_grade"] = int(assignment_df[problem_name + " 成績"])
        print(student_dict)
        
        return student_dict

def tokenlize(code):
    keywords = ['False', 'await', 'else', 'import', 'pass', 'None', 'break', 'except', 'in', 'raise', 'True', 'class', 'finally', 
                'is', 'return', 'and', 'continue', 'for', 'lambda', 'try', 'as', 'def', 'from', 'nonlocal', 'while', 'assert', 
                'del', 'global', 'not', 'with', 'async', 'elif', 'if', 'or', 'yield']

    built_in_function = ['abs', 'delattr', 'hash', 'memoryview', 'set', 'all', 'dict', 'help', 'min', 'setattr', 'any', 'dir',
                         'hex', 'next', 'slice', 'ascii', 'divmod', 'id', 'object', 'sorted', 'bin', 'enumerate', 'input', 'oct',
                         'staticmethod', 'bool', 'eval', 'int', 'open', 'str', 'breakpoint', 'exec', 'isinstance', 'ord', 'sum',
                         'bytearray', 'filter', 'issubclass', 'pow', 'super', 'bytes', 'float', 'iter', 'print', 'tuple', 'callable',
                         'format', 'len', 'property', 'type', 'chr',  'frozenset', 'list', 'range', 'vars', 'classmethod', 'getattr',
                         'locals', 'repr', 'zip', 'compile', 'globals', 'map', 'reversed', '__import__', 'complex', 'hasattr', 'max',
                         'round']

    tokens = []                               # for string tokens
    code_unit_list = re.findall("\s*(\d+|\w+|.)", code)
    # Loop through each source code word
    for unit_count in range(0, len(code_unit_list)):

        # This will check if a token has keyword
        if code_unit_list[unit_count] in keywords: 
            tokens.append(['KEYWORD', code_unit_list[unit_count]])
            continue
        
        # This will check if a token has built-in fuction
        if code_unit_list[unit_count] in built_in_function: 
            tokens.append(['FUNCTION', code_unit_list[unit_count]])
            continue
        
        # This will look for an identifier which would be just a word
        elif re.match("[a-z]", code_unit_list[unit_count]) or re.match("[A-Z]", code_unit_list[unit_count]):
            tokens.append(['IDENTIFIER', code_unit_list[unit_count]])
            continue

        # This will look for an operator
        elif code_unit_list[unit_count] in '*-/+%=':
            tokens.append(['OPERATOR', code_unit_list[unit_count]])
            continue

        # This will look for integer items and cast them as a number
        elif re.match("[0-9]+", code_unit_list[unit_count]):
            tokens.append(["INTEGER", code_unit_list[unit_count]])
            continue
            
        elif re.match("[.\'\"()]", code_unit_list[unit_count]):
            tokens.append(["SEPARATOR", code_unit_list[unit_count]])
            continue

    return tokens

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10011, debug=True)