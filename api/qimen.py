"""奇门遁甲 - 纯计算函数"""
import json
import datetime

try:
    from lunar_python import Solar, Lunar
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lunar-python', '-q'])
    from lunar_python import Solar, Lunar


# ===== 常量定义 =====
JIAZI = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

YANG_TERMS = {"冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
              "春分", "清明", "谷雨", "立夏", "小满", "芒种"}

JU_TABLE = {
    "阳遁": {
        "冬至": {"上元": 1, "中元": 7, "下元": 4},
        "小寒": {"上元": 2, "中元": 8, "下元": 5},
        "大寒": {"上元": 3, "中元": 9, "下元": 6},
        "立春": {"上元": 8, "中元": 5, "下元": 2},
        "雨水": {"上元": 9, "中元": 6, "下元": 3},
        "惊蛰": {"上元": 1, "中元": 7, "下元": 4},
        "春分": {"上元": 3, "中元": 9, "下元": 6},
        "清明": {"上元": 4, "中元": 1, "下元": 7},
        "谷雨": {"上元": 5, "中元": 2, "下元": 8},
        "立夏": {"上元": 4, "中元": 1, "下元": 7},
        "小满": {"上元": 5, "中元": 2, "下元": 8},
        "芒种": {"上元": 6, "中元": 3, "下元": 9},
    },
    "阴遁": {
        "夏至": {"上元": 9, "中元": 3, "下元": 6},
        "小暑": {"上元": 8, "中元": 2, "下元": 5},
        "大暑": {"上元": 7, "中元": 1, "下元": 4},
        "立秋": {"上元": 2, "中元": 5, "下元": 8},
        "处暑": {"上元": 1, "中元": 4, "下元": 7},
        "白露": {"上元": 9, "中元": 3, "下元": 6},
        "秋分": {"上元": 7, "中元": 1, "下元": 4},
        "寒露": {"上元": 6, "中元": 9, "下元": 3},
        "霜降": {"上元": 5, "中元": 8, "下元": 2},
        "立冬": {"上元": 6, "中元": 9, "下元": 3},
        "小雪": {"上元": 5, "中元": 8, "下元": 2},
        "大雪": {"上元": 4, "中元": 7, "下元": 1},
    },
}

EARTH_STEM_ORDER_YANG = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
EARTH_STEM_ORDER_YIN = ["戊", "乙", "丙", "丁", "癸", "壬", "辛", "庚", "己"]

PALACE_MAP = {
    1: {"name": "坎", "direction": "北", "element": "水"},
    2: {"name": "坤", "direction": "西南", "element": "土"},
    3: {"name": "震", "direction": "东", "element": "木"},
    4: {"name": "巽", "direction": "东南", "element": "木"},
    5: {"name": "中", "direction": "中", "element": "土"},
    6: {"name": "乾", "direction": "西北", "element": "金"},
    7: {"name": "兑", "direction": "西", "element": "金"},
    8: {"name": "艮", "direction": "东北", "element": "土"},
    9: {"name": "离", "direction": "南", "element": "火"},
}

STAR_NAMES = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
DOOR_NAMES = ["休门", "死门", "伤门", "杜门", "中门", "开门", "惊门", "生门", "景门"]
GOD_NAMES_YANG = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
GOD_NAMES_YIN = ["值符", "九天", "九地", "玄武", "白虎", "六合", "太阴", "螣蛇"]

XUNSHOU_TO_HIDDEN_YI = {
    "甲子": "戊", "甲戌": "己", "甲申": "庚",
    "甲午": "辛", "甲辰": "壬", "甲寅": "癸"
}

BRANCH_TO_PALACE = {
    "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4,
    "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6
}

TIANGAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}


def get_jiazi_index(gz):
    """获取干支在六十甲子中的索引"""
    try:
        return JIAZI.index(gz)
    except ValueError:
        return -1


def get_xun(gz):
    """获取旬"""
    idx = get_jiazi_index(gz)
    if idx == -1:
        return "甲子"
    return JIAZI[idx // 10 * 10]


def get_kongwang(gz):
    """获取旬空"""
    idx = get_jiazi_index(gz)
    if idx == -1:
        return ["戌", "亥"]
    xun_start = idx // 10 * 10
    last_two = JIAZI[xun_start + 10] if xun_start + 10 < 60 else JIAZI[(xun_start + 10) % 60]
    return [last_two[0], last_two[1]]


def calculate_qimen(body):
    now = datetime.datetime.now()
    year = int(body.get('year', now.year))
    month = int(body.get('month', now.month))
    day = int(body.get('day', now.day))
    hour = int(body.get('hour', now.hour))
    minute = int(body.get('minute', 0))
    question = body.get('question', '')
    question_type = body.get('question_type', 'general')

    # 用 lunar_python 获取干支信息
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = Lunar.fromSolar(solar)
    ec = lunar.getEightChar()

    # 节气
    jie_qi = lunar.getJieQi()
    active_jie = ""
    for jq in ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
               "春分", "清明", "谷雨", "立夏", "小满", "芒种",
               "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
               "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]:
        if jq in jie_qi:
            active_jie = jq

    # 阴阳遁
    dun_type = "阳遁" if active_jie in YANG_TERMS else "阴遁"

    # 三元
    day_gz = ec.getDay()
    day_idx = get_jiazi_index(day_gz)
    yuan_idx = (day_idx // 5) % 3 if day_idx >= 0 else 0
    yuan_map = {0: "上元", 1: "中元", 2: "下元"}
    yuan = yuan_map.get(yuan_idx, "上元")

    # 局数
    ju_number = JU_TABLE[dun_type][active_jie][yuan] if active_jie else 1

    # 时干支
    time_gz = ec.getTime()
    time_gan = time_gz[0]
    time_zhi = time_gz[1]

    # 旬首
    xun = get_xun(time_gz)
    xunshou = xun
    hidden_yi = XUNSHOU_TO_HIDDEN_YI.get(xun, "戊")
    kongwang = get_kongwang(time_gz)

    # 旬空宫位
    kongwang_palaces = [BRANCH_TO_PALACE.get(b, 0) for b in kongwang if b in BRANCH_TO_PALACE]

    # 地盘排布
    earth_order = EARTH_STEM_ORDER_YANG if dun_type == "阳遁" else EARTH_STEM_ORDER_YIN
    earth_plate = {}
    palace_order = list(range(ju_number, 10)) + list(range(1, ju_number))
    for i, palace_num in enumerate(palace_order):
        if i < len(earth_order):
            earth_plate[palace_num] = earth_order[i]

    # 值符/值使
    try:
        xun_gz_index = JIAZI.index(xunshou)
    except ValueError:
        xun_gz_index = 0
    xunshou_gan = xunshou[0]
    xunshou_zhi = xunshou[1]
    
    # 值符（星）: 旬首所在宫的原始星
    zhifu_star = "天蓬"  # default
    zhishi_door = "休门"  # default

    # 用神映射
    yongshen_map = {
        'career': '开门', 'money': '生门', 'love': '六合',
        'study': '景门', 'health': '天芮', 'travel': '生门',
        'lawsuit': '惊门', 'general': '时干'
    }
    yongshen = yongshen_map.get(question_type, '时干')

    # 九宫信息
    palaces = []
    for p_num in range(1, 10):
        if p_num == 5:
            continue  # 中宫寄坤
        palace = PALACE_MAP[p_num]
        earth_stem = earth_plate.get(p_num, "")
        palaces.append({
            'palace': p_num,
            'name': palace['name'],
            'direction': palace['direction'],
            'element': palace['element'],
            'earth_stem': earth_stem
        })

    return {
        'success': True,
        'data': {
            'time': f"{year}年{month}月{day}日 {hour:02d}:{minute:02d}",
            'ganzhi': {
                'year': ec.getYear(),
                'month': ec.getMonth(),
                'day': ec.getDay(),
                'hour': ec.getTime()
            },
            'jie_qi': active_jie,
            'dun_type': dun_type,
            'yuan': yuan,
            'ju_number': ju_number,
            'xunshou': xunshou,
            'hidden_yi': hidden_yi,
            'kongwang': kongwang,
            'kongwang_palaces': kongwang_palaces,
            'zhifu': zhifu_star,
            'zhishi': zhishi_door,
            'yongshen': yongshen,
            'palaces': palaces,
            'question': question,
            'question_type': question_type
        }
    }
