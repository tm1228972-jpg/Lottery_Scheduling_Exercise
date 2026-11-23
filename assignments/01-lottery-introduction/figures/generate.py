#!/usr/bin/env python3
"""Regenerate all 12 figures of Assignment 1 from the real experimental data.

    python3 figures/generate.py
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools'))
sys.path.insert(0, os.path.join(ROOT, 'code'))
os.chdir(REPO)
from reportkit import diagrams as D
from reportkit import theme

OUT = 'assignments/01-lottery-introduction/figures'
D.setup()
data = json.load(open('assignments/01-lottery-introduction/data/sim_results.json'))
C = theme.PALETTE

# 1. ticket distribution pie
D.pie([40, 30, 20, 10], ['فرآیند A', 'فرآیند B', 'فرآیند C', 'فرآیند D'], f'{OUT}/fig01_ticket_pie.png',
      'fa', 'توزیع بلیت‌ها بین چهار فرآیند', donut=True)

# 2. weighted measured vs expected bar groups
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportkit.fonts import register_matplotlib_fonts
register_matplotlib_fonts()
plt.rcParams['font.family'] = 'Vazirmatn'

w = data['weighted']
names = ['فرآیند A', 'فرآیند B', 'فرآیند C', 'فرآیند D']
fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=170)
import numpy as np
x = np.arange(len(names)); bw = 0.36
ax.bar(x - bw/2, w['expected'], bw, label='سهم انتظاری', color=C[0])
ax.bar(x + bw/2, [m['mean'] for m in w['measured']], bw, label='سهم اندازه‌گیری‌شده', color=C[1])
for i, m in enumerate(w['measured']):
    ax.text(i + bw/2, m['mean'] + 0.008, f"{m['mean']*100:.1f}%", ha='center', fontsize=7.4, color=theme.MUTED)
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=8.2)
ax.set_ylabel('سهم پردازنده', fontsize=8.6); ax.set_xlabel('فرآیند', fontsize=8.6)
ax.set_title('سهم انتظاری در برابر سهم واقعی (۴۰۰:۳۰۰:۲۰۰:۱۰۰)', fontsize=11, color=theme.ACCENT_DARK, fontweight='bold')
ax.legend(fontsize=8, frameon=False); ax.grid(axis='y', color='#e6edf2', lw=0.7); ax.set_axisbelow(True)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig(f'{OUT}/fig02_share_compare.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

# 3. convergence plot
rows = data['convergence']['rows']
plain = [(r['n'], r['error']) for r in rows if not r['compensated']]
comp  = [(r['n'], r['error']) for r in rows if r['compensated']]
fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=170)
ax.plot([p[0] for p in plain], [p[1] for p in plain], marker='o', ms=3.6, lw=1.8, color=C[1], label='قرعه‌کشی ساده')
ax.plot([p[0] for p in comp], [p[1] for p in comp], marker='s', ms=3.4, lw=1.8, color=C[0], label='با جبران تدریجی')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('تعداد قرعه‌کشی‌ها (مقیاس لگاریتمی)', fontsize=8.6)
ax.set_ylabel('بیشترین خطای سهم', fontsize=8.6)
ax.set_title('همگرایی خطای سهم در دو حالت', fontsize=11, color=theme.ACCENT_DARK, fontweight='bold')
ax.legend(fontsize=8, frameon=False); ax.grid(color='#e6edf2', lw=0.7, which='both'); ax.set_axisbelow(True)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig(f'{OUT}/fig03_convergence.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

# 4. load control
lc = data['load_control']['rows']
fig, ax = plt.subplots(figsize=(8.6, 3.7), dpi=170)
ax.plot([r['background_tickets'] for r in lc], [r['interactive_share'] for r in lc],
        marker='o', ms=5, lw=2, color=C[0], label='سهم اندازه‌گیری‌شده')
ax.plot([r['background_tickets'] for r in lc], [r['expected_share'] for r in lc],
        ls='--', lw=1.4, color=C[3], label='سهم انتظاری')
ax.set_xscale('log'); ax.set_xlabel('تعداد بلیت بار پس‌زمینه (مقیاس لگاریتمی)', fontsize=8.6)
ax.set_ylabel('سهم فرآیند تعاملی', fontsize=8.6)
ax.set_title('کنترل بار: حفظ سهم فرآیند تعاملی در برابر بار سنگین', fontsize=11, color=theme.ACCENT_DARK, fontweight='bold')
ax.legend(fontsize=8, frameon=False); ax.grid(color='#e6edf2', lw=0.7); ax.set_axisbelow(True)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig(f'{OUT}/fig04_load_control.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

# 5. flowchart of algorithm
D.flowchart(['شروع', 'تشکیل صف آماده با کلاینت‌ها', 'جمع تعداد بلیت‌های مؤثر',
             'آیا مجموع بلیت‌ها > ۰ است؟', 'قرعه‌کشی: انتخاب بلیت تصادفی',
             'پیمایش تجمعی برای یافتن برنده', 'اجرای برنده برای یک کوانتوم',
             'به‌روزرسانی آمار و بلیت‌های جبرانی', 'پایان'],
            f'{OUT}/fig05_algorithm_flow.png', 'fa', 'روند اجرای الگوریتم زمان‌بندی قرعه‌کشی',
            decision_at=3, branch_labels=('بله', 'خیر'), figsize=(9.6, 7.4))

# 6. architecture block diagram
D.block_diagram([('صف آماده\n(run queue)', 0.4, 2.2, 2.0, 1.1, 0),
                 ('محاسبه بلیت\nمؤثر', 2.9, 2.2, 2.0, 1.1, 1),
                 ('قرعه‌کشی\nتصادفی', 5.4, 2.2, 1.9, 1.1, 2),
                 ('زمان‌بند\nهسته', 7.8, 2.2, 1.8, 1.1, 3)],
            f'{OUT}/fig06_architecture.png', 'fa', 'جایگاه الگوریتم قرعه‌کشی در زمان‌بند هسته',
            arrows=[(2.4, 2.75, 2.9, 2.75), (4.9, 2.75, 5.4, 2.75), (7.3, 2.75, 7.8, 2.75)],
            figsize=(10, 3.6))

# 7. project gantt
D.gantt([('بررسی و مطالعه منابع', 0, 4), ('طراحی مدل بلیت و جبران', 4, 3),
         ('پیاده‌سازی شبیه‌ساز پایتون', 7, 6), ('پیاده‌سازی هسته C', 9, 5),
         ('اجرای آزمایش‌ها و تحلیل', 14, 4), ('نگارش گزارش دوزبانه', 18, 5),
         ('تهیه اسلاید و ارائه', 21, 2)],
        f'{OUT}/fig07_gantt.png', 'fa', 'نمودار گانت انجام تمرین اول', 'زمان (روز)', figsize=(10, 4.6))

# 8. waiting time distribution
wres = data['waiting']['rows']
fig, ax = plt.subplots(figsize=(8.6, 3.8), dpi=170)
short = [r['wait'] for r in wres if r['len'] <= 12]
long_ = [r['wait'] for r in wres if r['len'] > 12]
ax.bar(['کارهای کوتاه'] + [''] * (len(short) - 1), short, color=C[0], label='کار کوتاه')
plt.close(fig)
fig, ax = plt.subplots(figsize=(8.6, 3.8), dpi=170)
labels = [r['id'] for r in wres]
colors = [C[0] if r['len'] <= 12 else C[1] for r in wres]
ax.bar(labels, [r['wait'] for r in wres], color=colors, edgecolor='white', lw=0.7)
ax.set_ylabel('زمان انتظار (کوانتوم)', fontsize=8.6); ax.set_xlabel('کار', fontsize=8.6)
ax.set_title('زمان انتظار کارهای کوتاه (آبی) و بلند (نارنجی) با بلیت وزنی', fontsize=10.6, color=theme.ACCENT_DARK, fontweight='bold')
ax.grid(axis='y', color='#e6edf2', lw=0.7); ax.set_axisbelow(True); ax.tick_params(labelsize=7.8)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig(f'{OUT}/fig08_waiting.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

# 9. timeline of a draw sequence
segs = []
rng = __import__('random').Random(17)
names = ['A','B','C','D']
for i in range(24):
    segs.append((i, 1, names[rng.randrange(4)]))
D.timeline([('خط زمانی پردازنده', segs)], f'{OUT}/fig09_timeline.png', 'fa',
           'ترتیب اجرای برندگان در ۲۴ کوانتوم متوالی', horizon=24, unit='کوانتوم', figsize=(10, 2.6))

# 10. histogram of share error
errs_plain = []
errs_comp = []
for t in range(300):
    for comp, target in ((False, errs_plain), (True, errs_comp)):
        from lottery_sim import Client, LotteryScheduler
        import random as _r
        s = LotteryScheduler([Client('A',100), Client('B',100), Client('C',100)], compensation=comp, rng=_r.Random(500+t))
        s.run(300)
        target.append(max(abs(s.wins[k]/300 - 1/3) for k in 'ABC'))
D.histogram(errs_plain, errs_comp, ['قرعه‌کشی ساده', 'با جبران'], f'{OUT}/fig10_error_hist.png', 'fa',
            'توزیع خطای سهم در ۳۰۰ تکرار', 'خطای مطلق سهم', bins=26)

# 11. ticket inflation illustration
fig, ax = plt.subplots(figsize=(8.4, 3.5), dpi=170)
vals = [100, 200, 400, 800, 1600]
share_bg = [100/(100+v) for v in vals]
ax.plot(vals, share_bg, marker='o', lw=2, color=C[4])
ax.set_xlabel('تعداد بلیت فرآیند مزاحم', fontsize=8.6); ax.set_ylabel('سهم فرآیند اصلی', fontsize=8.6)
ax.set_title('اثر تورم بلیت: چرا سقف بلیت لازم است', fontsize=10.6, color=theme.ACCENT_DARK, fontweight='bold')
ax.grid(color='#e6edf2', lw=0.7); ax.set_axisbelow(True)
for xv, yv in zip(vals, share_bg):
    ax.annotate(f'{yv*100:.0f}%', (xv, yv), textcoords='offset points', xytext=(0,8), ha='center', fontsize=7.6, color=theme.MUTED)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig(f'{OUT}/fig11_inflation.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

# 12. state machine of client states
D.block_diagram([('آماده\nReady', 0.6, 3.0, 2.1, 1.0, 0), ('در حال اجرا\nRunning', 4.0, 3.0, 2.3, 1.0, 2),
                 ('مسدود\nBlocked', 7.4, 3.0, 2.1, 1.0, 1), ('پایان‌یافته\nTerminated', 4.0, 0.7, 2.3, 1.0, 3)],
            f'{OUT}/fig12_state_machine.png', 'fa', 'چرخه حالت کلاینت در زمان‌بند قرعه‌کشی',
            arrows=[(2.7,3.5,4.0,3.5),(6.3,3.5,7.4,3.5),(7.4,3.2,6.3,3.2),(5.1,3.0,5.1,1.7),(4.0,3.2,2.7,3.2)],
            figsize=(9, 4.4))

print('figures:', len([f for f in os.listdir(OUT) if f.endswith('.png')]))
