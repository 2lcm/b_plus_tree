import csv
import copy

verbal = True
# verbal = False

data_set = []


class Node(object):
    def __init__(self):
        self.parent = None
        self.next = None
        self.prev = None
        self.key = []
        # value : [[key, tid], [key, tid]]
        self.value = {}
        self.ch = []

    def is_leaf(self):
        return self.ch == []

    def most_left_key(self):
        if self.ch == []:
            return self.key[0]
        else:
            return self.ch[0].most_left_key()

    def set_key(self):
        if not self.is_leaf():
            self.key = []
            self.ch.sort(key=lambda x: x.key[0])
            for i in range(1, len(self.ch)):
                self.key.append(self.ch[i].most_left_key())

# iris data
# Id,SepalLengthCm,SepalWidthCm,PetalLengthCm,PetalWidthCm,Species
class Data(object):
    def __init__(self, _tid, _sepal_length, _sepal_width, _petal_length, _petal_width, _species):
        self.tid = _tid
        self.sepal_length = _sepal_length
        self.sepal_width = _sepal_width
        self.petal_length = _petal_length
        self.petal_width = _petal_width
        self.species = _species

    def key(self):
        return self.sepal_length, self.sepal_width


# B+-tree
class BP_tree(object):
    def __init__(self):
        self.root = Node()

    def load(self):
        global data_set
        try:
            self.root = Node()
            print('========== LOAD ===========')
            print('  LOAD_START_TID : ', end='')
            tid1 = int(input())
            print('  LOAD_END_TID   : ', end='')
            tid2 = int(input())
            print('LOADING...')

            assert(tid1 <= tid2)
            tid = 1
            with open('iris.csv', 'r') as csvfile:
                data_set = []
                reader = csv.reader(csvfile, delimiter=',')
                for line in reader:
                    if tid1 <= tid <= tid2:
                        # implementation
                        # initialize data_set from csv file
                        data = Data(int(line[0]), float(line[1]), float(line[2]), float(line[3]), float(line[4]), line[5])
                        data_set.append(data)
                        self.insert_data(data)
                    elif tid2 < tid:
                        break
                    tid += 1

            print('B+Tree is built')
        except ValueError:
            print('input value is wrong!')

    def print(self):
        cur_node = self.root
        i = 0
        while True:
            level_node = cur_node
            i += 1
            print('Level ', i, ':', end=' ')
            if cur_node.is_leaf():
                while True:
                    for key in cur_node.key:
                        print(key, cur_node.value[key], end=' ')
                    if cur_node.next is None:
                        break
                    cur_node = cur_node.next
                    print('->', end=' ')
                print(' ')
                break
            else:
                while True:
                    for key in cur_node.key:
                        print(key, end=' ')
                    if cur_node.next is None:
                        break
                    cur_node = cur_node.next
                    print('->', end=' ')
            cur_node = level_node.ch[0]
            print(' ')

    def insert(self):
        print('========== INSERT ==========')
        print('  TUPLE ID: ', end='')
        n = int(input())
        i = 1
        global data_set
        with open('iris.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for line in reader:
                if i == n:
                    data = Data(int(line[0]), float(line[1]), float(line[2]), float(line[3]), float(line[4]), line[5])
                    data_set.append(data)
                    self.insert_data(data)
                    break
                else:
                    i += 1
        print('TUPLE #' + str(n), 'is inserted.')

    def insert_data(self, data):
        assert(data is not None)
        cur_node = self.root
        # find right place
        key = data.key()
        while True:
            # must be leaf
            if cur_node.is_leaf():
                break
            elif key < cur_node.key[0]:
                cur_node = cur_node.ch[0]
            elif len(cur_node.key) == 1 or key < cur_node.key[1]:
                cur_node = cur_node.ch[1]
            else:
                cur_node = cur_node.ch[2]

        # now we are in leaf node
        assert(cur_node.is_leaf())

        if key in cur_node.key:
            cur_node.value[key].append(data.tid)
        else:
            cur_node.key.append(key)
            cur_node.key.sort()
            cur_node.value[key] = [data.tid]
            self.update(cur_node)

    def update(self, node):
        if node is None:
            return
        if len(node.ch) >= 2:
            node.set_key()
        case1 = node.is_leaf() and len(node.key) == 3
        case2 = (not node.is_leaf()) and len(node.ch) == 4
        case3 = node.is_leaf() and node.key == []
        case4 = (not node.is_leaf()) and (len(node.ch) == 1)
        parent = node.parent
        # overflow
        if case1 or case2:
            if node.parent is None:
                root_node = Node()
                root_node.ch.append(node)
                node.parent = root_node
                self.root = root_node

            new_node = Node()
            if node.next is not None:
                nxt = node.next
                new_node.next = nxt
                nxt.prev = new_node
            new_node.prev = node
            node.next = new_node
            new_node.parent = node.parent
            node.parent.ch.append(new_node)
            key = node.key.pop(2)
            new_node.key.append(key)
            if case1:
                new_node.value[key] = node.value.pop(key)
            else:
                tmp = node.ch.pop(2)
                tmp.parent = new_node
                new_node.ch.append(tmp)
                tmp = node.ch.pop(2)
                tmp.parent = new_node
                new_node.ch.append(tmp)
            node.set_key()
            new_node.set_key()
            node.parent.set_key()
        # underflow
        elif case3 or case4:
            nxt = node.next
            prev = node.prev
            if nxt is not None:
                nxt.prev = prev
            if prev is not None:
                prev.next = nxt
            idx = None
            if parent is not None:
                idx = parent.ch.index(node)
                parent.ch.remove(node)
                parent.set_key()
                assert (len(parent.ch) != 0)
            if case4:
                if parent is None:
                    root_node = node.ch[0]
                    self.root = root_node
                    root_node.parent = None
                else:
                    dic = {0: 0, 1: 0, 2: 1}
                    sibling = parent.ch[dic[idx]]
                    node.ch[0].parent = sibling
                    sibling.ch.append(node.ch[0])
                    self.update(sibling)
                    sibling.set_key()
        self.update(node.parent)

    def delete(self):
        print('========== DELETE ==========')
        print('  TUPLE ID: ', end='')
        tid = int(input())
        data = None
        global data_set
        for tmp in data_set:
            if tmp.tid == tid:
                data = tmp
                break
        if data is None:
            print('NOT FOUND')
            return

        # find leaf node
        key = data.key()
        cur_node = self.root
        while not cur_node.is_leaf():
            if key < cur_node.key[0]:
                cur_node = cur_node.ch[0]
            elif len(cur_node.key) == 1 or key < cur_node.key[1]:
                cur_node = cur_node.ch[1]
            else:
                cur_node = cur_node.ch[2]

        assert(key in cur_node.key)

        cur_node.value[key].remove(tid)
        if cur_node.value[key] == []:
            cur_node.key.remove(key)
            cur_node.value.pop(key)
            self.update(cur_node)

        data_set.remove(data)
        print('Tuple #'+str(tid), 'is deleted.')

    def search(self):
        print('========== SEARCH ==========')
        print('  SEARCH KEY (ex : 3.0 5.1): ', end='')
        key = tuple(map(float, input().split()))
        cur_node = self.root
        global data_set
        while True:
            if cur_node.is_leaf():
                if key in cur_node.key:
                    val = cur_node.value[key]
                    print('Found tuple IDs:', val)
                    print('Attributes: <sepal length, sepal width, petal length, petal width, species>')
                    for data in data_set:
                        if data.tid in val:
                            print('Tuple #'+str(data.tid), ': <',
                                  data.sepal_length, data.sepal_width, data.petal_length, data.petal_width,
                                  data.species, '>')
                else:
                    print('NOT FOUND')
                break
            else:
                if key < cur_node.key[0]:
                    cur_node = cur_node.ch[0]
                elif len(cur_node.key) == 1 or key < cur_node.key[1]:
                    cur_node = cur_node.ch[1]
                else:
                    cur_node = cur_node.ch[2]

    def range_search(self):
        global data_set
        print('======= RANGE SEARCH =======')
        print('  SEARCH KEY1 (ex : 3.0 5.1): ', end='')
        key1 = tuple(map(float, input().split()))
        print('  SEARCH KEY2 (ex : 3.0 5.1): ', end='')
        key2 = tuple(map(float, input().split()))
        key1, key2 = sorted((key1, key2))
        print('SEARCH RANGE:', key1, key2)
        cur_node = self.root
        val1 = []
        val2 = []
        while True:
            if cur_node.is_leaf():
                if key1 in cur_node.key:
                    loop = True
                    while loop:
                        for key in cur_node.key:
                            if key < key1:
                                continue
                            elif key2 < key:
                                loop = False
                                break
                            val1.append((key, cur_node.value[key]))
                            val2.extend(cur_node.value[key])
                        cur_node = cur_node.next
                        if cur_node is None:
                            break
                else:
                    print('NOT FOUND')
                break
            else:
                if key1 < cur_node.key[0]:
                    cur_node = cur_node.ch[0]
                elif len(cur_node.key) == 1 or key1 < cur_node.key[1]:
                    cur_node = cur_node.ch[1]
                else:
                    cur_node = cur_node.ch[2]

        print('Attributes: <sepal length, sepal width, petal length, petal width, species>')
        print('Found pairs:', val1)
        for data in data_set:
            if data.tid in val2:
                print('Tuple #' + str(data.tid), ': <',
                      data.sepal_length, data.sepal_width, data.petal_length, data.petal_width,
                      data.species, '>')

    def iterate(self):
        while True:
            print('===== B+ tree program ======')
            print('1. LOAD')
            print('2. PRINT')
            print('3. INSERT')
            print('4. DELETE')
            print('5. SEARCH')
            print('6. RANGE_SEARCH')
            print('7. EXIT')
            print('============================')
            print('SELECT MENU: ', end='')
            try:
                n = int(input())
                if n == 1:
                    self.load()
                elif n == 2:
                    self.print()
                elif n == 3:
                    self.insert()
                elif n == 4:
                    self.delete()
                elif n == 5:
                    self.search()
                elif n == 6:
                    self.range_search()
                elif n == 7:
                    break
                else:
                    print('wrong input, try again')
                assert(self.validate_check())
            except ValueError:
                print('wrong input, try again')

    def validate_check(self):
        level_node = self.root
        while not level_node.is_leaf():
            cur_node = level_node
            while True:
                for i in range(len(cur_node.key)):
                    if cur_node.key[i] != cur_node.ch[i+1].most_left_key():
                        return False
                    if len(cur_node.key) + 1 != len(cur_node.ch):
                        return False
                if cur_node.next is None:
                    break
                cur_node = cur_node.next
            level_node = level_node.ch[0]
        return True


if __name__ == '__main__':
    tree = BP_tree()
    tree.iterate()
