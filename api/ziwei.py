"""紫微斗数 - 纯计算函数"""
import json

try:
    from lunar_python import Solar, Lunar
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lunar-python', '-q'])
    from lunar_python import Solar, Lunar


# ===== 常量定义 =====
ZI_WEI_STARS = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞",
                "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]

MI_GONG = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 十四主星安星表（简化版）- 按紫微星所在宫位 + 五行局
# 紫微星定位是核心：根据五行局和农历生日
WU_XING_JU_MAP = {
    "水二局": 2, "木三局": 3, "金四局": 4, "土五局": 5, "火六局": 6
}

# 紫微星定位表：农历生日 + 五行局 -> 紫微星所在宫位（寅宫起1）
# 简化版本
ZI_WEI_POSITION_TABLE = {
    2:  {1: -1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11, 13: 12, 14: -1, 15: 1, 16: 2, 17: 3, 18: 4, 19: 5, 20: 6, 21: 7, 22: 8, 23: 9, 24: 10, 25: 11, 26: 12, 27: -1, 28: 1, 29: 2, 30: 3},
}

# 十二宫名称
PALACE_NAMES = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
                "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]


def calculate_ziwei(body):
    year = int(body.get('year', 1990))
    month = int(body.get('month', 1))
    day = int(body.get('day', 1))
    hour = int(body.get('hour', 12))
    minute = int(body.get('minute', 0))
    gender = int(body.get('gender', 0))

    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = Lunar.fromSolar(solar)
    ec = lunar.getEightChar()

    # 命宫地支
    ming_gong_zhi = ec.getMingGong()[-1] if ec.getMingGong() else "寅"
    shen_gong_zhi = ec.getShenGong()[-1] if ec.getShenGong() else "申"

    # 命宫索引
    ming_gong_index = MI_GONG.index(ming_gong_zhi) if ming_gong_zhi in MI_GONG else 2

    # 十二宫（逆时针排列，从命宫开始）
    palaces = []
    for i in range(12):
        idx = (ming_gong_index - i) % 12
        palaces.append({
            'name': PALACE_NAMES[i],
            'di_zhi': MI_GONG[idx],
            'stars': []
        })

    return {
        'success': True,
        'data': {
            'solar_date': f"{solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日",
            'lunar_date': '',
            'sizhu': {
                'year': ec.getYear(),
                'month': ec.getMonth(),
                'day': ec.getDay(),
                'hour': ec.getTime()
            },
            'ming_gong': ec.getMingGong(),
            'shen_gong': ec.getShenGong(),
            'ming_zhu': ec.getMingGong(),
            'shen_zhu': ec.getShenGong(),
            'tai_yuan': ec.getTaiYuan(),
            'palaces': palaces,
            'note': '紫微斗数完整排盘需要五行局计算、十四主星安星、辅星排布等复杂步骤。当前版本提供命宫身宫定位和十二宫框架，完整主星排盘正在开发中。'
        }
    }
