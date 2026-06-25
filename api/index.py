"""AI 术数 API — 八字·奇门·紫微 — Flask 版本"""
from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# ===== 引入各计算模块 =====
try:
    from lunar_python import Solar, Lunar, EightChar
    HAS_LUNAR = True
except ImportError:
    HAS_LUNAR = False


# ======================== 八字排盘 ========================

def calc_bazi(data):
    if not HAS_LUNAR:
        return {'success': False, 'error': 'lunar_python 未安装'}

    year = int(data.get('year', 1990))
    month = int(data.get('month', 1))
    day = int(data.get('day', 1))
    hour = int(data.get('hour', 12))
    minute = int(data.get('minute', 0))
    gender = int(data.get('gender', 0))

    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = Lunar.fromSolar(solar)
    ec = lunar.getEightChar()
    yun = ec.getYun(gender)

    sizhu = {}
    for k, func in [('year', ec.getYear), ('month', ec.getMonth), ('day', ec.getDay), ('hour', ec.getTime)]:
        gz = func()
        sizhu[k] = {
            'gan_zhi': gz,
            'tian_gan': gz[0] if gz else '',
            'di_zhi': gz[1] if len(gz) > 1 else '',
        }

    shishen = {}
    pillar_map = {'year': 'Year', 'month': 'Month', 'day': 'Day', 'hour': 'Time'}
    for k, attr in pillar_map.items():
        shishen[k] = {
            'tian_gan': getattr(ec, f'get{attr}ShiShenGan')(),
            'di_zhi': getattr(ec, f'get{attr}ShiShenZhi')(),
        }

    dayun_list = []
    for dy in yun.getDaYun():
        dayun_list.append({
            'gan_zhi': dy.getGanZhi(),
            'start_age': dy.getStartAge(),
            'end_age': dy.getEndAge()
        })

    return {'success': True, 'data': {
        'solar_date': f"{solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日",
        'lunar_date': str(lunar),
        'sizhu': sizhu,
        'shishen': shishen,
        'start_year': yun.getStartYear(),
        'dayun': dayun_list,
        'tai_yuan': ec.getTaiYuan(),
        'ming_gong': ec.getMingGong(),
        'shen_gong': ec.getShenGong(),
    }}


# ======================== 奇门遁甲 ========================

JIAZI = ["甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
         "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
         "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
         "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
         "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
         "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥"]

YANG_TERMS = {"冬至","小寒","大寒","立春","雨水","惊蛰",
              "春分","清明","谷雨","立夏","小满","芒种"}

JU_TABLE = {"阳遁": {"冬至":{"上元":1,"中元":7,"下元":4},"小寒":{"上元":2,"中元":8,"下元":5},"大寒":{"上元":3,"中元":9,"下元":6},"立春":{"上元":8,"中元":5,"下元":2},"雨水":{"上元":9,"中元":6,"下元":3},"惊蛰":{"上元":1,"中元":7,"下元":4},"春分":{"上元":3,"中元":9,"下元":6},"清明":{"上元":4,"中元":1,"下元":7},"谷雨":{"上元":5,"中元":2,"下元":8},"立夏":{"上元":4,"中元":1,"下元":7},"小满":{"上元":5,"中元":2,"下元":8},"芒种":{"上元":6,"中元":3,"下元":9}},
            "阴遁": {"夏至":{"上元":9,"中元":3,"下元":6},"小暑":{"上元":8,"中元":2,"下元":5},"大暑":{"上元":7,"中元":1,"下元":4},"立秋":{"上元":2,"中元":5,"下元":8},"处暑":{"上元":1,"中元":4,"下元":7},"白露":{"上元":9,"中元":3,"下元":6},"秋分":{"上元":7,"中元":1,"下元":4},"寒露":{"上元":6,"中元":9,"下元":3},"霜降":{"上元":5,"中元":8,"下元":2},"立冬":{"上元":6,"中元":9,"下元":3},"小雪":{"上元":5,"中元":8,"下元":2},"大雪":{"上元":4,"中元":7,"下元":1}}}

EARTH_ORDER_YANG = ["戊","己","庚","辛","壬","癸","丁","丙","乙"]
EARTH_ORDER_YIN  = ["戊","乙","丙","丁","癸","壬","辛","庚","己"]

PALACE_INFO = {1:"坎·北·水",2:"坤·西南·土",3:"震·东·木",4:"巽·东南·木",
               6:"乾·西北·金",7:"兑·西·金",8:"艮·东北·土",9:"离·南·火"}

XUNSHOU_YI = {"甲子":"戊","甲戌":"己","甲申":"庚","甲午":"辛","甲辰":"壬","甲寅":"癸"}
BRANCH_PALACE = {"子":1,"丑":8,"寅":8,"卯":3,"辰":4,"巳":4,"午":9,"未":2,"申":2,"酉":7,"戌":6,"亥":6}

YONGSHEN_MAP = {'career':'开门','money':'生门','love':'六合','study':'景门','health':'天芮','travel':'生门','lawsuit':'惊门','general':'时干'}


def calc_qimen(data):
    if not HAS_LUNAR:
        return {'success': False, 'error': 'lunar_python 未安装'}

    now = datetime.datetime.now()
    dt = {'year': int(data.get('year', now.year)),
          'month': int(data.get('month', now.month)),
          'day': int(data.get('day', now.day)),
          'hour': int(data.get('hour', now.hour)),
          'minute': int(data.get('minute', 0))}

    solar = Solar.fromYmdHms(dt['year'], dt['month'], dt['day'], dt['hour'], dt['minute'], 0)
    lunar = Lunar.fromSolar(solar)
    ec = lunar.getEightChar()

    # 节气
    jie_qi = lunar.getJieQi()
    active_jie = ""
    for jq in ["冬至","小寒","大寒","立春","雨水","惊蛰","春分","清明","谷雨",
               "立夏","小满","芒种","夏至","小暑","大暑","立秋","处暑","白露",
               "秋分","寒露","霜降","立冬","小雪","大雪"]:
        if jq in jie_qi:
            active_jie = jq

    dun_type = "阳遁" if active_jie in YANG_TERMS else "阴遁"

    day_gz = ec.getDay()
    day_idx = JIAZI.index(day_gz) if day_gz in JIAZI else 0
    yuan = ["上元","中元","下元"][(day_idx // 5) % 3]
    ju = JU_TABLE[dun_type].get(active_jie, {}).get(yuan, 1)
    time_gz = ec.getTime()
    xun = JIAZI[(JIAZI.index(time_gz) // 10) * 10] if time_gz in JIAZI else "甲子"
    kw = [JIAZI[JIAZI.index(xun) + 10][0], JIAZI[JIAZI.index(xun) + 10][1]] if JIAZI.index(xun) + 10 < 60 else ["戌","亥"]

    palaces = []
    for p in [1,2,3,4,6,7,8,9]:
        parts = PALACE_INFO[p].split('·')
        palaces.append({
            'palace': p, 'name': parts[0], 'direction': parts[1], 'element': parts[2]
        })

    return {'success': True, 'data': {
        'time': f"{dt['year']}年{dt['month']}月{dt['day']}日 {dt['hour']:02d}:{dt['minute']:02d}",
        'ganzhi': {'year': ec.getYear(), 'month': ec.getMonth(), 'day': day_gz, 'hour': time_gz},
        'jie_qi': active_jie, 'dun_type': dun_type, 'yuan': yuan, 'ju_number': ju,
        'xunshou': xun, 'kongwang': kw,
        'yongshen': YONGSHEN_MAP.get(data.get('question_type','general'),'时干'),
        'palaces': palaces,
    }}


# ======================== 紫微斗数 ========================

def calc_ziwei(data):
    if not HAS_LUNAR:
        return {'success': False, 'error': 'lunar_python 未安装'}

    year = int(data.get('year', 1990))
    month = int(data.get('month', 1))
    day = int(data.get('day', 1))
    hour = int(data.get('hour', 12))
    minute = int(data.get('minute', 0))

    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = Lunar.fromSolar(solar)
    ec = lunar.getEightChar()

    MI_GONG = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    PALACE_NAMES = ["命宫","兄弟宫","夫妻宫","子女宫","财帛宫","疾厄宫",
                    "迁移宫","交友宫","官禄宫","田宅宫","福德宫","父母宫"]

    mg_zhi = ec.getMingGong()[-1] if ec.getMingGong() and len(ec.getMingGong()) > 1 else "寅"
    mg_idx = MI_GONG.index(mg_zhi) if mg_zhi in MI_GONG else 2

    palaces = []
    for i in range(12):
        idx = (mg_idx - i) % 12
        palaces.append({'name': PALACE_NAMES[i], 'di_zhi': MI_GONG[idx]})

    return {'success': True, 'data': {
        'solar_date': f"{solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日",
        'ming_gong': ec.getMingGong(),
        'shen_gong': ec.getShenGong(),
        'tai_yuan': ec.getTaiYuan(),
        'palaces': palaces,
    }}


# ======================== Flask 路由 ========================

@app.route('/api/bazi', methods=['POST', 'OPTIONS'])
def api_bazi():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(calc_bazi(request.get_json(silent=True) or {}))

@app.route('/api/qimen', methods=['POST', 'OPTIONS'])
def api_qimen():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(calc_qimen(request.get_json(silent=True) or {}))

@app.route('/api/ziwei', methods=['POST', 'OPTIONS'])
def api_ziwei():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(calc_ziwei(request.get_json(silent=True) or {}))


# Vercel 需要这个
app.debug = False
