"""八字排盘 - 纯计算函数"""
import json

try:
    from lunar_python import Solar, Lunar, EightChar
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lunar-python', '-q'])
    from lunar_python import Solar, Lunar, EightChar


def calculate_bazi(body):
    year = int(body.get('year', 1990))
    month = int(body.get('month', 1))
    day = int(body.get('day', 1))
    hour = int(body.get('hour', 12))
    minute = int(body.get('minute', 0))
    gender = int(body.get('gender', 0))  # 0=男, 1=女
    calendar_type = body.get('calendar_type', 'solar')  # solar or lunar

    try:
        if calendar_type == 'lunar':
            lunar = Lunar.fromYmd(year, month, day)
            solar = lunar.getSolar()
            solar_hour = hour
        else:
            solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
            lunar = Lunar.fromSolar(solar)
    except Exception as e:
        # fallback
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = Lunar.fromSolar(solar)

    ec = lunar.getEightChar()
    yun = ec.getYun(gender)
    
    # 四柱
    sizhu = {
        'year': {'gan_zhi': ec.getYear(), 'tian_gan': ec.getYearGan(), 'di_zhi': ec.getYearZhi(),
                 'wu_xing': ec.getYearWuXing(), 'na_yin': ec.getYearNaYin(),
                 'cang_gan': ec.getYearHideGan()},
        'month': {'gan_zhi': ec.getMonth(), 'tian_gan': ec.getMonthGan(), 'di_zhi': ec.getMonthZhi(),
                  'wu_xing': ec.getMonthWuXing(), 'na_yin': ec.getMonthNaYin(),
                  'cang_gan': ec.getMonthHideGan()},
        'day': {'gan_zhi': ec.getDay(), 'tian_gan': ec.getDayGan(), 'di_zhi': ec.getDayZhi(),
                'wu_xing': ec.getDayWuXing(), 'na_yin': ec.getDayNaYin(),
                'cang_gan': ec.getDayHideGan()},
        'hour': {'gan_zhi': ec.getTime(), 'tian_gan': ec.getTimeGan(), 'di_zhi': ec.getTimeZhi(),
                 'wu_xing': ec.getTimeWuXing(), 'na_yin': ec.getTimeNaYin(),
                 'cang_gan': ec.getTimeHideGan()}
    }

    # 十神
    shishen = {
        'year': {'tian_gan': ec.getYearShiShenGan(), 'di_zhi': ec.getYearShiShenZhi()},
        'month': {'tian_gan': ec.getMonthShiShenGan(), 'di_zhi': ec.getMonthShiShenZhi()},
        'day': {'tian_gan': ec.getDayShiShenGan(), 'di_zhi': ec.getDayShiShenZhi()},
        'hour': {'tian_gan': ec.getTimeShiShenGan(), 'di_zhi': ec.getTimeShiShenZhi()}
    }

    # 五行统计
    wuxing_map = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    for pillar in [ec.getYear(), ec.getMonth(), ec.getDay(), ec.getTime()]:
        for char in pillar:
            if char in '甲乙': wuxing_map['木'] += 1
            elif char in '丙丁': wuxing_map['火'] += 1
            elif char in '戊己': wuxing_map['土'] += 1
            elif char in '庚辛': wuxing_map['金'] += 1
            elif char in '壬癸': wuxing_map['水'] += 1

    # 大运
    dayun_list = []
    dayun = yun.getDaYun()
    for dy in dayun:
        dayun_list.append({
            'gan_zhi': dy.getGanZhi(),
            'start_age': dy.getStartAge(),
            'end_age': dy.getEndAge()
        })

    # 流年（当前年份+前后5年）
    import datetime
    current_year = datetime.datetime.now().year
    liunian_list = []
    for y in range(current_year - 3, current_year + 4):
        liunian_list.append({'year': y, 'gan_zhi': ec.getYear()})  # simplified

    # 胎元 & 命宫
    tai_yuan = ec.getTaiYuan()
    ming_gong = ec.getMingGong()
    
    return {
        'success': True,
        'data': {
            'solar_date': f"{solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日",
            'lunar_date': lunar.toFullString().split(' ')[0] if hasattr(lunar, 'toFullString') else '',
            'sizhu': sizhu,
            'shishen': shishen,
            'wuxing_stats': wuxing_map,
            'tai_yuan': tai_yuan,
            'ming_gong': ming_gong,
            'shen_gong': ec.getShenGong(),
            'start_year': yun.getStartYear(),
            'dayun': dayun_list,
            'current_year': current_year
        }
    }
