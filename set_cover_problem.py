__author__ = "jiaying"


import random
import time
import numpy as np
import matplotlib.pylab as plt
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value


def generate_data_set(num_elements, num_subsets=0): # 隨機生成全域集合(全域集合中元素的數量)
    universe = list(range(1, num_elements + 1))

    # 隨機生成子集合
    all_elements = []
    if num_subsets == 0:
        num_subsets =  random.randint(1, num_elements)  # 子集合的數量
    subsets = {}
    for i in range(1, num_subsets + 1):
        subset_size = random.randint(1, num_elements // 2)  # 子集合大小隨機範圍
        subsets[i] = random.sample(universe, subset_size)
        all_elements.extend(subsets[i])
        
    if set(universe) != set(all_elements): # 子集合聯集是否包含所有元素
        uncover = [set(universe) - set(all_elements)]
        for i in uncover[0]:
            chose_subset = random.randint(1, num_subsets)
            subsets[chose_subset].append(i)
    
    return subsets


def greedy_set_cover(set_system):
    universe = set()
    for subset in set_system:
        universe.update(set_system[subset])

    selected_subsets = set()
    uncovered_elements = set(universe)

    while uncovered_elements:
        best_subset = None
        max_covered = 0

        for subset in set_system:
            covered_elements = set(set_system[subset]).intersection(uncovered_elements)
            if len(covered_elements) > max_covered:
                max_covered = len(covered_elements)
                best_subset = subset

        if best_subset is None:
            break

        selected_subsets.add(best_subset)
        uncovered_elements.difference_update(set(set_system[best_subset]))

    return selected_subsets


def random_approximation(set_system):
    universe = set()
    for subset in set_system:
        universe.update(set_system[subset])

    selected_subsets = set()
    uncovered_elements = set(universe)

    while uncovered_elements:
        subset = random.choice(list(set_system.keys()))
        selected_subsets.add(subset)
        uncovered_elements -= set(set_system[subset])

    return selected_subsets


def integer_linear_programming(set_system):
    # 構建問題
    problem = LpProblem("Set_Cover_Problem", LpMinimize)

    # 構建變量
    subset_vars = LpVariable.dicts("Subset", set_system, cat="Binary")

    # 定義目標函數
    problem += lpSum(subset_vars)

    # 定義約束條件
    universe = set()
    for subset in set_system:
        universe.update(set_system[subset])

    for element in universe:
        problem += lpSum(subset_vars[subset] for subset in set_system if element in set_system[subset]) >= 1

    # 解決問題
    problem.solve()

    # 輸出結果
    result = {
        'status': problem.status,
        'objective_value': value(problem.objective),
        'selected_subsets': []
    }

    for subset in set_system:
        if value(subset_vars[subset]) == 1:
            result['selected_subsets'].append(subset)

    return result


#實驗主程式
subsets_dict = {}
result = {}
use_time = {'greedy':[], 'Randomized':[], 'Linear':[]} 
for i in range(10):
    subsets = generate_data_set(1000,100)
    subsets_dict["test_data" + str(i)] = subsets
    
    start = time.time()
    greedy_selected_subsets = greedy_set_cover(subsets)
    end = time.time()
    use_time['greedy'].append(end - start)
    start = time.time()
    rand_selected_subsets = random_approximation(subsets)
    end = time.time()
    use_time['Randomized'].append(end - start)
    start = time.time()
    ilp_selected_subsets = set(integer_linear_programming(subsets)['selected_subsets'])
    end = time.time()
    use_time['Linear'].append(end - start)
    
    result["test" + str(i+1)] = {}
    result["test" + str(i+1)]["greedy"] = {'selected_subsets': greedy_selected_subsets, "len": len(greedy_selected_subsets)}
    result["test" + str(i+1)]['Randomized'] = {'selected_subsets': rand_selected_subsets, "len": len(rand_selected_subsets)}
    result["test" + str(i+1)]['Linear'] = {'selected_subsets': ilp_selected_subsets, "len": len(ilp_selected_subsets)}
    
    
    print("test" + str(i+1))
    print("greedy Selected subsets:", greedy_selected_subsets)
    print("random_approximation Selected subsets:", rand_selected_subsets)
    print("integer_linear_programming Selected subsets:", ilp_selected_subsets)
    print()

#計算次數與平均
count = {}
for i in result:
    test_result = result[i]
    for j in test_result:
        if j not in count:
            count[j] = []
        count[j].append(test_result[j]['len'])

count_avg = {}
for i in count:
    count_avg[i] = sum(count[i])/len(count[i])

#畫圖:平均次數
myList = count_avg.items()
myList = sorted(myList) 
x, y = zip(*myList) 
plt.figure(figsize=(10,6))
plt.xlabel('Algorithm')
plt.ylabel('number')
plt.plot(x, y)
plt.savefig('count_avg1000.png')  
plt.show()
print(count_avg)

#畫圖:每次實驗次數
x = range(1,11)
y1 = count['greedy']
y2 = count['Randomized']
y6 = count['Linear']
plt.figure(figsize=(10,6))
plt.plot(x,y1,label="greedy")
plt.plot(x,y2,label="Randomized")
plt.plot(x,y6,label="Linear")
plt.xlabel("times",fontsize=13)
plt.ylabel("number",fontsize=13)
plt.legend()
plt.savefig('number1000.png')  
plt.show()

#計算平均執行時間
time_avg = {}
for i in use_time:
    time_avg[i] = round(sum(use_time[i])/len(use_time[i]),5)
print(time_avg)

#畫圖:各演算法每次實驗時間
x = range(1,11)
y1 = use_time['greedy']
y2 = use_time['Randomized']
y6 = use_time['Linear']
plt.figure(figsize=(10,6))
plt.plot(x,y1,label="greedy")
plt.plot(x,y2,label="Randomized")
plt.plot(x,y6,label="Linear")
plt.xlabel("times",fontsize=13)
plt.ylabel("seconds",fontsize=13)
plt.legend()
plt.savefig('seconds1000.png')  
plt.show()