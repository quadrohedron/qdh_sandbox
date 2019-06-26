import sys, time, random, math, copy
from PIL import Image, ImageQt
from PySide2.QtCore import Qt, QByteArray, QRectF, QSize, QTimer
from PySide2.QtWidgets import QApplication, QGraphicsOpacityEffect, QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QSpinBox, QStackedLayout, QTabWidget, QWidget
from PySide2.QtGui import QColor, QPainter, QPixmap

######################################################################################################


BASE36 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
          'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
COLOURS_H = ['#000000', '#df00ff', '#2000ff', '#009fff', '#00ff9f', '#20ff00', '#dfff00', '#ff6000', '#ff0060',
             '#ef80ff', '#8f80ff', '#80cfff', '#80ffcf', '#8fff80', '#efff80', '#ffaf80', '#ff80af']


def hsv2rgb(*hsv):
    h, s, v = hsv[0] if len(hsv) == 1 else hsv
    hi = math.floor(h * 6) % 6
    vmin = (1 - s) * v
    a = (v - vmin) * ((6 * h) % 1)
    if hi == 0:
        return (v, vmin + a, vmin)
    elif hi == 1:
        return (v - a, v, vmin)
    elif hi == 2:
        return (vmin, v, vmin + a)
    elif hi == 3:
        return (vmin, v - a, v)
    elif hi == 4:
        return (vmin + a, vmin, v)
    else:
        return (v, vmin, v - a)


def rgb2hex(*rgb):
    if len(rgb) == 1:
        rgb = rgb[0]
    res = '#'
    for i in rgb:
        el = hex(int(round(i * 255, 0)))[2:]
        if len(el) == 1:
            el = '0' + el
        res += el
    return res


def hsv2hex(*hsv):
    return rgb2hex(hsv2rgb(hsv))


def cellcolourH(val):
    if val:
        s = 0.5 ** ((val - 1) // 8)
        h = abs(0.9375 - (val % 8) / 8)
        return hsv2hex(h, s, 1)
    else:
        return '#000000'


def generate_xpm(p):
    codes = {}
    for i in p.c:
        for j in i:
            codes[j] = 1
    colnum = len(codes)
    chardepth = 1
    while 36 ** chardepth < colnum:
        chardepth += 1
    for i, key in enumerate(codes):
        code = ''
        for j in range(chardepth):
            i, codepoint = divmod(i, 36)
            code += BASE36[codepoint]
        codes[key] = (code, cellcolourH(key))
    xp = p.expand()
    h, w = len(xp), len(xp[0])
    res = [' '.join(map(str, [w, h, colnum, chardepth]))]
    for key in codes:
        code = codes[key]
        res.append('{0} c {1}'.format(code[0], code[1]))
    for y in range(h):
        l = ''
        for x in range(w):
            l += codes[xp[y][x]][0]
        res.append(l)
    return res, (w, h)


########################

class o4i:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = self.n = len(t)
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m = self.m
        t = [[-1 for i in range(2 * m - 1)] for j in range(2 * m - 1)]
        for i in range(m):
            for j in range(i + 1):
                t[i + m - 1][j + m - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(i):
                t[j + m - 1][i + m - 1] = self.c[i][j]
        for i in range(m):
            for j in range(1, m):
                t[i + m - 1][m - 1 - j] = t[i + m - 1][j + m - 1]
        for i in range(1, m):
            for j in range(2 * m - 1):
                t[m - 1 - i][j] = t[i + m - 1][j]
        return t

    def topple(self):
        if self.v:
            print('\nOctopile topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(i + 1)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            if self.c[-1][i] > 3:
                self.m += 1
                self.c.append([0 for j in range(self.m)])
                d.append([0 for j in range(self.m)])
                break
        for i in range(self.m):
            for j in range(i + 1):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 4 * v
                    for k, l in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        if j + l == 0:
                            if i + k == 0:
                                d[0][0] += 4 * v
                            elif 0 < i + k < self.m:
                                d[i + k][0] += 2 * v if l else v
                        elif -1 < i + k and 0 < j + l < i + k + 1:
                            d[i + k][j + l] += 2 * v if i + k == j + l else v
        if not c:
            for i in range(self.m):
                for j in range(i + 1):
                    self.c[i][j] += d[i][j]
            return True
        return False


class o4f:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m = self.m
        t = [[None for j in range(2 * m - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(i + 1):
                t[i + m - 1][j + m - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(i):
                t[j + m - 1][i + m - 1] = self.c[i][j]
        for i in range(m):
            for j in range(1, m):
                t[i + m - 1][m - 1 - j] = t[i + m - 1][j + m - 1]
        for i in range(1, m):
            for j in range(2 * m - 1):
                t[m - 1 - i][j] = t[i + m - 1][j]
        return t

    def topple(self):
        if self.v:
            print('\nOctofixed topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(i + 1)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(i + 1):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 4 * v
                    for k, l in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        if j + l == 0:
                            if i + k == 0:
                                d[0][0] += 4 * v
                            elif 0 < i + k < self.m:
                                d[i + k][0] += 2 * v if l else v
                        elif -1 < i + k < self.m and -1 < j + l < i + k + 1:
                            d[i + k][j + l] += 2 * v if i + k == j + l else v
        if not c:
            for i in range(self.m):
                for j in range(i + 1):
                    self.c[i][j] += d[i][j]
            return True
        return False


class o8i:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = self.n = len(t)
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m = self.m
        t = [[-1 for i in range(2 * m - 1)] for j in range(2 * m - 1)]
        for i in range(m):
            for j in range(i + 1):
                t[i + m - 1][j + m - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(i):
                t[j + m - 1][i + m - 1] = self.c[i][j]
        for i in range(m):
            for j in range(1, m):
                t[i + m - 1][m - 1 - j] = t[i + m - 1][j + m - 1]
        for i in range(1, m):
            for j in range(2 * m - 1):
                t[m - 1 - i][j] = t[i + m - 1][j]
        return t

    def topple(self):
        if self.v:
            print('\nO8P topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(i + 1)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            if self.c[-1][i] > 7:
                self.m += 1
                self.c.append([0 for j in range(self.m)])
                d.append([0 for j in range(self.m)])
                break
        for i in range(self.m):
            for j in range(i + 1):
                if self.c[i][j] > 7:
                    c = False
                    v = self.c[i][j] // 8
                    if j + 1 == i:
                        if j:
                            m = 7
                        else:
                            m = 6
                    else:
                        m = 8
                    d[i][j] -= m * v
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if k == 0 == l:
                                continue
                            if -1 < i + k and -1 < j + l < i + k + 1:
                                if j + l == 0:
                                    if i + k == 0:
                                        d[0][0] += 4 * v
                                    else:
                                        d[i + k][0] += 2 * v if l else v
                                else:
                                    d[i + k][j + l] += 2 * v if (i + k == j + l and k - l != 0) else v
        if not c:
            for i in range(self.m):
                for j in range(i + 1):
                    self.c[i][j] += d[i][j]
            return True
        return False


class o8f:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m = self.m
        t = [[None for j in range(2 * m - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(i + 1):
                t[i + m - 1][j + m - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(i):
                t[j + m - 1][i + m - 1] = self.c[i][j]
        for i in range(m):
            for j in range(1, m):
                t[i + m - 1][m - 1 - j] = t[i + m - 1][j + m - 1]
        for i in range(1, m):
            for j in range(2 * m - 1):
                t[m - 1 - i][j] = t[i + m - 1][j]
        return t

    def topple(self):
        if self.v:
            print('\nO8F topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(i + 1)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(i + 1):
                if self.c[i][j] > 7:
                    c = False
                    v = self.c[i][j] // 8
                    if j + 1 == i:
                        if j:
                            m = 7
                        else:
                            m = 6
                    else:
                        m = 8
                    d[i][j] -= m * v
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if k == 0 == l:
                                continue
                            if -1 < i + k < self.m and -1 < j + l < i + k + 1:
                                if j + l == 0:
                                    if i + k == 0:
                                        d[0][0] += 4 * v
                                    else:
                                        d[i + k][0] += 2 * v if l else v
                                else:
                                    d[i + k][j + l] += 2 * v if (i + k == j + l and k - l != 0) else v
        if not c:
            for i in range(self.m):
                for j in range(i + 1):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t4i:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nTetrapile topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.n):
            if self.c[-1][i] > 3:
                self.m += 1
                self.c.append([0 for j in range(self.n)])
                d.append([0 for j in range(self.n)])
                break
        for i in range(self.m):
            if self.c[i][-1] > 3:
                self.n += 1
                for j in range(self.m):
                    self.c[j].append(0)
                for j in range(self.m):
                    d[j].append(0)

                break
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 4 * v
                    for k, l in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                            continue
                        # print(self.m,i,k,';',self.n,j,l,';',len(d),len(d[0]))
                        d[i + k][j + l] += 2 * v if (i > i + k == 0 or j > j + l == 0) else v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
                    # print(self.c[i][j],end=' ')
                # print()
            # print('\n\n')
            return True
        return False


class t4f:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                # print(m,i,';',n,j,'...',i+m-1,j+n-1)
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nTetrafixed topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 4 * v
                    for k, l in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                            continue
                        # print(self.m,i,k,';',self.n,j,l)
                        d[i + k][j + l] += 2 * v if (i > i + k == 0 or j > j + l == 0) else v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
                    # print(self.c[i][j],end=' ')
                # print()
            # print('\n\n')
            return True
        return False


class t4ie:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n)] for i in range(2 * m)]
        for i in range(m):
            for j in range(n):
                t[i + m][j + n] = self.c[i][j]
        for i in range(m):
            for j in range(n):
                t[-i + m - 1][j + n] = t[i + m][j + n]
        for i in range(2 * m):
            for j in range(n):
                t[i][-j + n - 1] = t[i][j + n]
        return t

    def topple(self):
        if self.v:
            print('\nEven tetrapile topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.n):
            if self.c[-1][i] > 3:
                self.m += 1
                self.c.append([0 for j in range(self.n)])
                d.append([0 for j in range(self.n)])
                break
        for i in range(self.m):
            if self.c[i][-1] > 3:
                self.n += 1
                for j in range(self.m):
                    self.c[j].append(0)
                for j in range(self.m):
                    d[j].append(0)

                break
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 4 * v
                    for k, l in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                            continue
                        d[i + k][j + l] += v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t4fe:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n)] for i in range(2 * m)]
        for i in range(m):
            for j in range(n):
                t[i + m][j + n] = self.c[i][j]
        for i in range(m):
            for j in range(n):
                t[-i + m - 1][j + n] = t[i + m][j + n]
        for i in range(2 * m):
            for j in range(n):
                t[i][-j + n - 1] = t[i][j + n]
        return t

    def topple(self):
        if self.v:
            print('\nEven tetrapile topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 2 * v
                    if i:
                        d[i][j] -= v
                    if j:
                        d[i][j] -= v
                    for k, l in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                            continue
                        d[i + k][j + l] += v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t6hi:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nT6P topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.n):
            if self.c[-1][i] > 5:
                self.m += 1
                self.c.append([0 for j in range(self.n)])
                d.append([0 for j in range(self.n)])
                break
        for i in range(self.m):
            if self.c[i][-1] > 5:
                self.n += 1
                for j in range(self.m):
                    self.c[j].append(0)
                for j in range(self.m):
                    d[j].append(0)

                break
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 5:
                    c = False
                    v = self.c[i][j] // 6
                    d[i][j] -= 6 * v
                    for k in range(-1, 2):
                        for l in range(-1, 2, 2):
                            if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                                continue
                            if (j == 1 and l == -1) or (i == 1 and k == -1):
                                if i + j + k + l or k == 0:
                                    m = 2
                                else:
                                    m = 4
                            else:
                                m = 1
                            d[i + k][j + l] += m * v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t6hf:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nT6F topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 5:
                    c = False
                    v = self.c[i][j] // 6
                    d[i][j] -= 6 * v
                    for k in range(-1, 2):
                        for l in range(-1, 2, 2):
                            if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                                continue
                            if (j == 1 and l == -1) or (i == 1 and k == -1):
                                if i + j + k + l or k == 0:
                                    m = 2
                                else:
                                    m = 4
                            else:
                                m = 1
                            d[i + k][j + l] += m * v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t6vi:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nT6P topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.n):
            if self.c[-1][i] > 5:
                self.m += 1
                self.c.append([0 for j in range(self.n)])
                d.append([0 for j in range(self.n)])
                break
        for i in range(self.m):
            if self.c[i][-1] > 5:
                self.n += 1
                for j in range(self.m):
                    self.c[j].append(0)
                for j in range(self.m):
                    d[j].append(0)

                break
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 5:
                    c = False
                    v = self.c[i][j] // 6
                    d[i][j] -= 6 * v
                    for k in range(-1, 2, 2):
                        for l in range(-1, 2):
                            if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                                continue
                            if (j == 1 and l == -1) or (i == 1 and k == -1):
                                if i + j + k + l or l == 0:
                                    m = 2
                                else:
                                    m = 4
                            else:
                                m = 1
                            d[i + k][j + l] += m * v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t6vf:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nT6F topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 5:
                    c = False
                    v = self.c[i][j] // 6
                    d[i][j] -= 6 * v
                    for k in range(-1, 2, 2):
                        for l in range(-1, 2):
                            if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                                continue
                            if (j == 1 and l == -1) or (i == 1 and k == -1):
                                if i + j + k + l or l == 0:
                                    m = 2
                                else:
                                    m = 4
                            else:
                                m = 1
                            d[i + k][j + l] += m * v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class t8f:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t[0])
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m, n = self.m, self.n
        t = [[None for j in range(2 * n - 1)] for i in range(2 * m - 1)]
        for i in range(m):
            for j in range(n):
                t[i + m - 1][j + n - 1] = self.c[i][j]
        for i in range(1, m):
            for j in range(n):
                t[-i + m - 1][j + n - 1] = t[i + m - 1][j + n - 1]
        for i in range(2 * m - 1):
            for j in range(1, n):
                t[i][-j + n - 1] = t[i][j + n - 1]
        return t

    def topple(self):
        if self.v:
            print('\nT6F topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(self.n)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(self.n):
                if self.c[i][j] > 7:
                    c = False
                    v = self.c[i][j] // 8
                    d[i][j] -= 8 * v
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if k == 0 == l or i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= self.n:
                                continue
                            if (j == 1 and l == -1) or (i == 1 and k == -1):
                                if i + j + k + l or k == 0 or l == 0:
                                    m = 2
                                else:
                                    m = 4
                            else:
                                m = 1
                            d[i + k][j + l] += m * v
        if not c:
            for i in range(self.m):
                for j in range(self.n):
                    self.c[i][j] += d[i][j]
            return True
        return False


class tr4f:
    def __init__(self, t, frozen=False, timed=True, vocal=True):
        self.i = -1
        self.c = t
        self.t = time.time() if timed else None
        self.m = len(t)
        self.n = len(t)
        self.v = vocal
        if not frozen:
            self.topple()

    def expand(self):
        m = self.m
        t = [[None for i in range(2 * m - 1)] for j in range(2 * m - 1)]
        for i in range(m):
            for j in range(2 * i + 1):
                t[i + m - 1][j + m - 1 - i] = self.c[i][j]
        for i in range(1, m):
            for j in range(2 * i):
                t[j - i + m - 1][i + m - 1] = self.c[i][j]
        for i in range(2 * m - 2):
            for j in range(i + 1):
                t[i - j][j] = t[-j + 2 * m - 2][j - i + 2 * m - 2]
        return t

    def topple(self):
        if self.v:
            print('\nTetrafixed topples...')
        while self.topple_step():
            pass
        if self.v:
            print('F I N I S H E D\nin', self.i, 'iterations.')
            if self.t:
                print('Time to topple:', time.time() - self.t)
                self.t = None

    def topple_step(self):
        self.i += 1
        d = [[0 for j in range(2 * i + 1)] for i in range(self.m)]
        c = True
        if self.v and not self.i % 1000:
            print('Iteration', self.i, 't:', time.time())
        for i in range(self.m):
            for j in range(2 * i + 1):
                if self.c[i][j] > 3:
                    c = False
                    v = self.c[i][j] // 4
                    d[i][j] -= 4 * v
                    for k, l in ((-1, -1), (1, 1), (0, -1), (0, 1)):
                        if i + k < 0 or i + k >= self.m or j + l < 0 or j + l >= 2 * (i + k) + 1:
                            continue
                        if i + k == 0 == j + l:
                            m = 4
                        elif j + l == 0 or j + l == 2 * (i + k):
                            m = 2
                        else:
                            m = 1
                        d[i + k][j + l] += m * v
        if not c:
            for i in range(self.m):
                for j in range(2 * i + 1):
                    self.c[i][j] += d[i][j]
            return True
        return False


######################################################################################################

# Key codes
_M = 77
_R = 82
_SPACE = 32
_CTRL = 16777249
_ALT = 16777251
_F11 = 16777274

# Ignore this
_X = 80
_Y = 45


class SSApp(QApplication):
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.mainwidget = SandyScreen(self)
        sys.exit(self.exec_())


class SandyMenu(QWidget):
    def __init__(self, parent):
        pass
        QWidget.__init__(self, parent)
        self.root = parent

        self.piletype = None

        # Initialising UI
        self.init_ui()

    def init_ui(self):
        # Menu grid layout and its settings
        grid = QGridLayout(self)
        grid.setColumnMinimumWidth(4, 260)
        grid.setColumnStretch(4, 0)
        for i in [1, 2, 3, 5]:
            grid.setColumnMinimumWidth(i, 75)
            grid.setColumnStretch(i, 0)
        for i in [0, 6]:
            grid.setColumnStretch(i, 1)
        grid.setRowMinimumHeight(1, 360)
        grid.setRowMinimumHeight(2, 25)
        for i in [0, 3]:
            grid.setRowStretch(i, 1)

        # Widgets
        self.tabw = QTabWidget(self)
        grid.addWidget(self.tabw, 1, 1, 1, 5)
        self.tabs = {}
        self.tabs['pile'] = QWidget(self)
        self.pilegrid = QGridLayout(self.tabs['pile'])
        self.pilegrid.setRowStretch(6, 1)
        self.tabw.addTab(self.tabs['pile'], 'Sandpile')
        self.tabs['visl'] = QWidget(self)
        self.vslgrid = QGridLayout(self.tabs['visl'])
        self.tabw.addTab(self.tabs['visl'], 'Visual')

        self.pilegrid.addWidget(QLabel('Seed:', self.tabs['pile']), 0, 0, 1, 1)
        self.pilegrid.addWidget(QLabel('Type:', self.tabs['pile']), 2, 0, 1, 1)

        self.seedfield = QLineEdit(self.tabs['pile'])
        self.pilegrid.addWidget(self.seedfield, 1, 0, 1, 4)

        self.buttons = {}
        self.buttons['cont'] = QPushButton('Continue', self)
        def func1():
            self.root.toggle_menu()
            self.root.toggle_pause()
        self.buttons['cont'].clicked.connect(func1)
        grid.addWidget(self.buttons['cont'], 2, 1, 1, 1)
        self.buttons['rest'] = QPushButton('Restart', self)
        def func2():
            self.root.restart_pile()
            func1()
        self.buttons['rest'].clicked.connect(func2)
        grid.addWidget(self.buttons['rest'], 2, 2, 1, 1)
        self.buttons['roll'] = QPushButton('Reset', self)
        def func3():
            txt = self.seedfield.text()
            try:
                seed = eval(txt)
            except:
                seed = [[8]]
            self.root.reroll_pile(piletype = self.piletype, seed = seed)
            func1()
        self.buttons['roll'].clicked.connect(func3)
        grid.addWidget(self.buttons['roll'], 2, 3, 1, 1)
        self.buttons['clsm'] = QPushButton('Close Menu', self)
        self.buttons['clsm'].clicked.connect(self.root.toggle_menu)
        grid.addWidget(self.buttons['clsm'], 2, 5, 1, 1)

        self.typeradios = {}
        for i, key in enumerate(['o4i','o4f','o8i','o8f']):
            b = QRadioButton(key, self.tabs['pile'])
            self.typeradios[key] = b
            self.pilegrid.addWidget(b, 3, i, 1, 1)
        for i, key in enumerate(['t4i','t4f','t8f']):
            b = QRadioButton(key, self.tabs['pile'])
            self.typeradios[key] = b
            self.pilegrid.addWidget(b, 4, i, 1, 1)
        for i, key in enumerate(['t6hi','t6hf','t6vi','t6vf']):
            b = QRadioButton(key, self.tabs['pile'])
            self.typeradios[key] = b
            self.pilegrid.addWidget(b, 5, i, 1, 1)
        for k in self.typeradios:
            b = self.typeradios[k]
            b.clicked.connect(self.set_piletype)

        self.vslgrid.addWidget(QLabel('Timed delay:', self.tabs['visl']), 0, 0, 1, 1)
        self.vslgrid.addWidget(QLabel('Frames per step:', self.tabs['visl']), 1, 0, 1, 1)
        self.vslgrid.setRowStretch(2, 1)
        self.vslgrid.setColumnStretch(2, 1)

        self.tdspinbox = QSpinBox(self.tabs['visl'])
        self.tdspinbox.setMinimum(10)
        self.tdspinbox.valueChanged.connect(self.set_td)
        self.vslgrid.addWidget(self.tdspinbox, 0, 1, 1, 1)

        self.fpsspinbox = QSpinBox(self.tabs['visl'])
        self.fpsspinbox.setMinimum(1)
        self.fpsspinbox.setMaximum(300)
        self.fpsspinbox.valueChanged.connect(self.set_fps)
        self.vslgrid.addWidget(self.fpsspinbox, 1, 1, 1, 1)

    def set_piletype(self):
        for k in self.typeradios:
            b = self.typeradios[k]
            if b.isChecked():
                self.piletype = eval(b.text())
                break

    def set_fps(self):
        self.root.delta_per_tick = 1 / self.fpsspinbox.value()

    def set_td(self):
        self.root.timer_delay = self.tdspinbox.value()


class SandyScreen(QWidget):
    def __init__(self, root):
        QWidget.__init__(self)
        self.root = root

        # Setting state vars
        self.app_running = True
        self.ctrl_down = False
        self.in_fullscreen = False
        self.in_menu = False
        self.on_pause = True

        # Setting animation vars
        self.timer_delay = 10
        self.phase = 1
        self.delta_per_tick = 1 / 30
        self.xpmsz = None
        self.geo = [0, 0, 0, 0]

        # Creating timer and sandpile
        self.timer = QTimer(self)
        self.seed = None
        self.piletype = None
        self.sandpile = None
        self.reroll_pile()

        # Generating pause icon
        self.pause_icon = Image.new('RGBA', size=(60, 60))
        for i in range(60):
            for j in range(60):
                self.pause_icon.putpixel((j, i), (255, 255, 255, 0 if 20 < j < 40 else 100))

        # Initialising UI and running
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setMinimumSize(600, 400)
        self.setWindowTitle('Sandy Screen')

        # Menu widget
        self.menu = SandyMenu(self)

        # Sandbox container widget and its background and canvas label stack
        self.sandbox = QWidget(self)
        self.sandbox.setGeometry(0, 0, 600, 400)
        self.sandbox_bg = QLabel(self.sandbox)
        self.sandbox_bg.setGeometry(0, 0, 600, 400)
        self.sandbox_bg.setPixmap(QPixmap(['1 1 1 1', '1 c #000000', '1']).scaled(self.sandbox_bg.size()))
        self.canvases = [QLabel(self.sandbox), QLabel(self.sandbox)]
        for c in self.canvases:
            c.setAlignment(Qt.AlignCenter)
            c.setGeometry(0, 0, 600, 400)
        self.canvases[1].setPixmap(QPixmap(generate_xpm(self.sandpile)[0]))
        self.sandpile.topple_step()
        self.canvases[0].setPixmap(QPixmap(generate_xpm(self.sandpile)[0]))

        # Opacity effect on the upper frame label
        self.opeff = QGraphicsOpacityEffect(self.canvases[-1])
        self.opeff.setOpacity(1)
        self.canvases[-1].setGraphicsEffect(self.opeff)

        # Main stack layout
        self.layout = QStackedLayout(self)
        self.layout.addWidget(self.sandbox)
        self.layout.addWidget(self.menu)

        # Overlay pause icon label
        self.pause_label = QLabel(self)
        self.pause_label.setAlignment(Qt.AlignCenter)
        self.pause_label.setPixmap(QPixmap(ImageQt.ImageQt(self.pause_icon)))

    def restart_pile(self):
        del self.sandpile
        self.sandpile = self.piletype(copy.deepcopy(self.seed), frozen = True, timed = False, vocal = False)
        print('restart called')

    def reroll_pile(self, piletype = None, seed = None):
        if seed:
            self.seed = seed
        else:
            v = random.randint(8, 33)
            self.seed = [[v for j in range(_X)] for i in range(_Y)]
        if piletype:
            self.piletype = piletype
        else:
            v = random.randint(0, 3)
            self.piletype = [t4f, t6hf, t6vf, t8f][v]
        self.sandpile = self.piletype(copy.deepcopy(self.seed), frozen = True, timed = False, vocal = False)

    def run(self):
        self.root.exec_()

    def closeEvent(self, event):
        self.timer.stop()
        self.app_running = False

    def keyPressEvent(self, event):
        k = event.key()
        if k == 16777236:
            self.update_sandbox(1)  #
        if k == _CTRL:
            self.ctrl_down = True
        if self.ctrl_down:
            if k == _M:
                self.toggle_menu()  # Menu toggled on Ctrl+M
            elif k == _R:
                self.reroll_pile()
        else:
            if k == _F11:
                self.toggle_fullscreen()
            elif k == _SPACE and not self.in_menu:
                self.toggle_pause()

    def keyReleaseEvent(self, event):
        if event.key() == _CTRL:
            self.ctrl_down = False

    def resizeEvent(self, event):
        self.pause_label.setGeometry(self.rect())
        sbg = self.sandbox.geometry()
        sbs = self.sandbox.size()
        self.sandbox_bg.setGeometry(sbg)
        self.sandbox_bg.setPixmap(self.sandbox_bg.pixmap().scaled(self.sandbox_bg.size()))
        for c in self.canvases:
            c.setGeometry(sbg)
            c.setPixmap(c.pixmap().scaled(sbs, Qt.KeepAspectRatio))
        ### Fix this.

    def toggle_fullscreen(self):
        self.in_fullscreen = not self.in_fullscreen
        self.showFullScreen() if self.in_fullscreen else self.showNormal()

    def toggle_menu(self):
        self.in_menu = not self.in_menu
        if self.in_menu:
            self.layout.setCurrentIndex(1)
            self.pause_label.setVisible(False)
            self.on_pause = True
            self.root.restoreOverrideCursor()
        else:
            self.layout.setCurrentIndex(0)
            if self.on_pause:
                self.pause_label.raise_()
                self.pause_label.setVisible(True)
            else:
                self.root.setOverrideCursor(Qt.BlankCursor)
        self.resizeEvent(None)

    def toggle_pause(self):
        self.on_pause = not self.on_pause
        if self.on_pause:
            self.timer.stop()
            self.pause_label.raise_()
            self.pause_label.setVisible(True)
            self.root.restoreOverrideCursor()
        else:
            self.pause_label.setVisible(False)
            self.timer.singleShot(self.timer_delay, lambda: self.update_sandbox(0))
            self.root.setOverrideCursor(Qt.BlankCursor)

    def update_sandbox(self, mode):
        if not self.in_menu:
            if mode == self.on_pause:
                self.phase -= self.delta_per_tick
                if self.phase <= 0:
                    self.canvases[-1].setPixmap(self.canvases[0].pixmap())
                    self.phase = 1
                    self.opeff.setOpacity(self.phase)
                    if not self.sandpile.topple_step() and not self.on_pause:
                        self.toggle_pause()
                    xpm, sz = generate_xpm(self.sandpile)
                    self.canvases[0].setPixmap(QPixmap(xpm).scaled(self.sandbox.size(), Qt.KeepAspectRatio))
                else:
                    self.opeff.setOpacity(math.pow(math.sin(math.pi * self.phase / 2), 2))
                if mode == 0 and self.app_running:
                    self.timer.singleShot(self.timer_delay, lambda: self.update_sandbox(0))


if __name__ == '__main__':
    app = SSApp(sys.argv)
