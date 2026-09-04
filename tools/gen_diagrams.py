# -*- coding: utf-8 -*-
"""生成项目文档所需的 6 张图表 PNG（供 Word 文档嵌入）。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle
import os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "assets")
os.makedirs(OUT, exist_ok=True)

C_CLIENT = "#E8F1FF"; E_CLIENT = "#2F6FED"
C_SRV    = "#FFF4E5"; E_SRV    = "#E8890C"
C_BE     = "#F0FFF4"; E_BE     = "#2E9E5B"
C_NET    = "#F5F5F7"; E_NET    = "#8A8A8E"
C_ZONE   = "#FDF2F8"; E_ZONE   = "#DB2777"
ARROW    = "#374151"


def box(ax, x, y, w, h, text, fc, ec, fs=11, lw=1.6, weight="bold", style="round,pad=0.02"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=lw,
                                mutation_scale=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            weight=weight, linespacing=1.5)


def arrow(ax, x1, y1, x2, y2, text=None, fs=9, rad=0.0, color=ARROW, ls="-", loff=(0, 0.06)):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.4, color=color, linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((x1 + x2) / 2 + loff[0], (y1 + y2) / 2 + loff[1], text, ha="center",
                va="center", fontsize=fs, color=color, weight="bold",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=1.5))


def newfig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------- 1 架构图
def arch_overview():
    fig, ax = newfig(11, 7.8)
    ax.text(50, 97, "山海企划义卖系统 · 总体架构", ha="center", fontsize=17, weight="bold")

    box(ax, 8, 80, 30, 12, "客户端（顾客）\n微信小程序\n登录·围栏·浏览·下单·2FA码", C_CLIENT, E_CLIENT, 10.5)
    box(ax, 62, 80, 30, 12, "员工端（分区角色）\n同一小程序·JWT权限\n检票·校验·配货打票·核销·发放", C_CLIENT, E_CLIENT, 10.5)

    box(ax, 2, 42, 24, 22, "前1服务器 F1\nshs-trade\n交易与库存权威\n登记·限购·原子扣减\n订单WAL·可靠投递", C_SRV, E_SRV, 10)
    box(ax, 38, 42, 24, 22, "前2服务器 F2\nshs-catalog\n目录服务\n商品/图片/静态资源\n库存只读副本", C_SRV, E_SRV, 10)
    box(ax, 74, 42, 24, 22, "后端服务器 BE\nshs-core\n订单账本（唯一事实）\n员工WS·纪念品台账\n监控大屏·应急开关", C_BE, E_BE, 10)

    # F1 ↔ BE 走线（下方总线，避开 F2）
    for xx in (14, 86):
        ax.plot([xx, xx], [42, 31], color=ARROW, lw=1.2, ls=":")
    arrow(ax, 14, 36, 86, 36, "HTTPS 批量投递 + 断网重发（保序）", 9)
    arrow(ax, 86, 31, 14, 31, "← HTTPS 核销回传（释放缓存）", 9)
    # F1 → F2 库存推送
    arrow(ax, 26, 53, 38, 53, "WS 库存推送≤1s", 8.5)
    # 客户端 / 员工端 → 服务器
    arrow(ax, 14, 80, 12, 64, "HTTPS\n登记/下单", 9, loff=(-4.5, 0))
    arrow(ax, 28, 80, 47, 64, "HTTPS 匿名浏览商品/库存", 9)
    arrow(ax, 64, 80, 22, 64, "HTTPS 队列校验", 9)
    arrow(ax, 72, 80, 54, 64, "WSS 库存订阅", 9, loff=(0, 0.4))
    arrow(ax, 84, 80, 86, 64, "WSS 订单 / HTTPS 核销", 9, loff=(1.5, 0))

    box(ax, 24, 14, 50, 10, "现场内网（AP ×3 + 交换机 + QCI6 CPE 出口）\n192.168.10.0/24 · 全链路 TLS1.3", C_NET, E_NET, 10, weight="normal")
    box(ax, 79, 14, 17, 10, "公网\nNTP 对时/证书\n（仅经 CPE）", "white", E_NET, 9, weight="normal")
    arrow(ax, 72, 19, 79, 19, "NTP", 9)
    save(fig, "arch_overview.png")


# ---------------------------------------------------------------- 2 网络拓扑
def network_topology():
    fig, ax = newfig(11.5, 7.2)
    ax.text(50, 96, "现场网络拓扑 · 192.168.10.0/24", ha="center", fontsize=17, weight="bold")

    box(ax, 42, 84, 16, 8, "Internet", "white", E_NET, 11, weight="normal")
    box(ax, 26, 70, 20, 8, "QCI6 CPE 主\n192.168.10.2", C_NET, E_NET, 10, weight="normal")
    box(ax, 54, 70, 20, 8, "QCI6 CPE 备(冷备)\n192.168.10.3", C_NET, E_NET, 10, weight="normal")
    box(ax, 40, 57, 20, 8, "核心路由/防火墙\n192.168.10.1", C_NET, E_NET, 10, weight="normal")

    box(ax, 12, 42, 22, 8, "交换机 SW1(千兆)", C_NET, E_NET, 10, weight="normal")
    box(ax, 64, 42, 24, 8, "PoE 交换机 SW2", C_NET, E_NET, 10, weight="normal")

    for i, (x, t) in enumerate([(2, "F1 交易\n.21"), (17, "F2 目录\n.22"), (32, "BE 账本\n.23"), (47, "运维本\n.30")]):
        fc, ec = (C_BE, E_BE) if t.startswith(("F1", "F2", "BE")) else ("white", E_NET)
        box(ax, x, 26, 13, 9, t, fc, ec, 10)

    for x, t in [(60, "AP-1 入口/队伍"), (74, "AP-2 提货/纪念"), (88, "AP-3 浏览/机动")]:
        box(ax, x, 26, 11.5, 9, t, C_NET, E_NET, 8.8, weight="normal")

    box(ax, 60, 6, 39.5, 12, "员工终端 ×10（DHCP .100-.149，SH-Staff 隐藏SSID）\n顾客终端（SH-Guest 开放SSID，.150-.250，仅放行443）", "white", E_NET, 9.5, weight="normal")

    arrow(ax, 50, 84, 38, 78, "主", 9)
    arrow(ax, 50, 84, 62, 78, "备", 9, ls="--")
    arrow(ax, 40, 70, 49, 65); arrow(ax, 60, 70, 51, 65)
    arrow(ax, 45, 57, 25, 50); arrow(ax, 55, 57, 74, 50)
    for x in (8.5, 23.5, 38.5, 53.5):
        arrow(ax, 20, 42, x, 35)
    for x in (65.5, 79.5, 93.5):
        arrow(ax, 76, 42, x, 35)
    arrow(ax, 72, 26, 76, 18); arrow(ax, 88, 26, 86, 18)
    ax.text(50, 2, "防火墙策略：顾客段仅可达 F1/F2:443；服务器互访白名单；SSH 仅运维机", ha="center", fontsize=9.5, color="#555")
    save(fig, "network_topology.png")


# ---------------------------------------------------------------- 3 下单时序
def sequence_order():
    fig, ax = newfig(11, 8.2)
    ax.text(50, 97, "下单主链路时序（含断网重发语义）", ha="center", fontsize=17, weight="bold")
    xs = {"客户": 12, "F1": 33, "F2": 52, "BE": 70, "员工": 89}
    for name, x in xs.items():
        fc, ec = (C_CLIENT, E_CLIENT) if name == "客户" else (C_BE, E_BE) if name == "员工" else (C_SRV, E_SRV)
        box(ax, x - 7, 88, 14, 6, name, fc, ec, 11)
        ax.plot([x, x], [6, 88], color="#9CA3AF", lw=1.2, ls="--", zorder=1)

    steps = [
        ("客户", "F2", "① GET 商品+库存（缓存优先）", "ret"),
        ("F2", "客户", "② 返回列表+剩余库存", None),
        ("客户", "F1", "③ POST /orders {wxid, fp, items}", None),
        ("F1", "F1", "④ 三重校验·原子扣减·WAL落盘", "self"),
        ("F1", "客户", "⑤ 201 {order_id}(P99≤500ms)", None),
        ("F1", "F2", "⑥ WS inventory.delta(≤1s)", "ret"),
        ("F1", "BE", "⑦ POST /internal/orders/batch", None),
        ("BE", "BE", "⑧ ULID幂等落库(SQLite)", "self"),
        ("BE", "F1", "⑨ ACK{order_ids} → 清缓存", "ret"),
        ("BE", "员工", "⑩ WSS order.new", None),
        ("员工", "员工", "11) 打印小票 → order.printed 回执", "self"),
    ]
    y = 82
    for src, dst, label, kind in steps:
        if kind == "self":
            bx = xs[src] + 1.5 if xs[src] + 17 <= 100 else xs[src] - 17
            box(ax, bx, y - 1.6, 15.5, 3.4, label, "#FEF9C3", "#CA8A04", 8.6, weight="normal", style="round,pad=0.01")
        else:
            x1, x2 = xs[src], xs[dst]
            ls = "--" if "WS" in label or "WSS" in label else "-"
            ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=13,
                                         lw=1.5, color=ARROW, linestyle=ls))
            ax.text((x1 + x2) / 2, y + 1.1, label, ha="center", fontsize=9.2, weight="bold")
        y -= 6.6
    ax.text(50, 3, "断网重发：⑦失败 → 指数退避(1s/2s/4s/5s)顺序重投未ACK批次 → 恢复后≤30s追平 → BE补推员工端补打",
            ha="center", fontsize=10, color="#B91C1C", weight="bold")
    save(fig, "sequence_order.png")


# ---------------------------------------------------------------- 4 订单状态机
def state_machine():
    fig, ax = newfig(10.5, 5.4)
    ax.text(50, 94, "订单状态机", ha="center", fontsize=17, weight="bold")

    box(ax, 6, 55, 20, 12, "BUFFERED\n（F1受理·已扣库存\n已落WAL）", C_SRV, E_SRV, 10.5)
    box(ax, 40, 55, 20, 12, "SYNCED\n（BE幂等落库\n账本唯一事实）", C_SRV, E_SRV, 10.5)
    box(ax, 74, 55, 20, 12, "FULFILLED\n（提货核销\n释放F1缓存资源）", C_BE, E_BE, 10.5)
    box(ax, 40, 15, 20, 12, "CANCELLED\n（ADMIN作废\n回补库存）", "#FEE2E2", "#DC2626", 10.5)

    arrow(ax, 26, 61, 40, 61, "批量投递+ACK(≤2s)", 9.5, loff=(0, 0.9))
    arrow(ax, 60, 61, 74, 61, "员工扫客户2FA核销", 9.5, loff=(0, 0.9))
    arrow(ax, 50, 55, 50, 27, "作废(留痕)", 9.5, loff=(3.5, 0))
    ax.add_patch(FancyArrowPatch((8, 55), (42, 20), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.4, color=ARROW, connectionstyle="arc3,rad=-0.15"))
    ax.text(17, 36, "BE不可达时停留\n（WAL保序重投）", fontsize=9, color="#555", ha="center")
    ax.text(50, 6, "侧态：printed（打印回执，BE记录 printed_at）；outbox.state: PENDING→INFLIGHT→SYNCED（投递通道）",
            ha="center", fontsize=9.5, color="#555")
    box(ax, 2, 80, 12, 7, "[开始]\n顾客下单", "white", "#9CA3AF", 9.5, weight="normal")
    arrow(ax, 10, 80, 12, 67)
    save(fig, "state_machine.png")


# ---------------------------------------------------------------- 5 甘特图
def gantt():
    fig, ax = plt.subplots(figsize=(11.5, 6.8))
    tasks = [
        ("需求/架构/契约冻结(M1)", 0, 1, "JOINT"),
        ("shs-crypto 2FA库+金样本", 0.6, 0.6, "A"),
        ("F1 登记+库存SSOT+下单", 1.3, 1.2, "A"),
        ("F1 WAL可靠投递 + BE落库(M2)", 2.4, 1.2, "A"),
        ("F2 目录/静态/库存WS", 3.6, 0.9, "A"),
        ("BE 员工WS/核销/纪念品/管理台", 4.4, 1.0, "A"),
        ("压测与混沌注入(M4)", 5.4, 1.0, "A"),
        ("小程序骨架/登录/围栏", 1.0, 0.8, "B"),
        ("浏览/下单/2FA组件", 1.7, 1.3, "B"),
        ("入场扫码/指纹/校时", 2.9, 1.0, "B"),
        ("员工端六区页面", 4.1, 1.0, "B"),
        ("蓝牙打印+WS客户端", 4.9, 0.8, "B"),
        ("真机测试/组网验证", 5.6, 1.4, "B"),
        ("全链路联调(M3)", 4.1, 1.2, "JOINT"),
        ("两轮现场彩排(M5)", 6.0, 1.0, "JOINT"),
        ("上线保障与复盘(M6)", 7.0, 1.0, "JOINT"),
    ]
    colors = {"A": "#3B82F6", "B": "#22C55E", "JOINT": "#F59E0B"}
    ypos = {t[0]: len(tasks) - i for i, t in enumerate(tasks)}
    for name, start, dur, who in tasks:
        ax.barh(ypos[name], dur, left=start, height=0.62, color=colors[who], alpha=0.9, edgecolor="white")
        ax.text(start + dur + 0.06, ypos[name], f"{dur:g}周", va="center", fontsize=8.5, color="#555")
    ax.set_yticks(list(ypos.values()))
    ax.set_yticklabels(list(ypos.keys()), fontsize=10)
    ax.set_xlim(0, 8.6); ax.set_xticks(range(0, 9))
    ax.set_xticklabels([f"W{i}" if i else "启动" for i in range(0, 9)], fontsize=10)
    ax.grid(axis="x", ls="--", alpha=0.4)
    for m, wk, label in [("M1", 1, "M1 契约冻结"), ("M2", 3, "M2 主链路"), ("M3", 5, "M3 全功能"),
                         ("M4", 6, "M4 压测达标"), ("M5", 7, "M5 彩排通过"), ("M6", 8, "M6 上线")]:
        ax.axvline(wk, color="#DC2626", ls=":", lw=1.4)
        ax.text(wk, len(tasks) + 0.7, label, ha="center", fontsize=9, color="#DC2626", weight="bold")
    import matplotlib.patches as mpatches
    ax.legend(handles=[mpatches.Patch(color=c, label=l) for c, l in
                       [("#3B82F6", "A · Rust后端"), ("#22C55E", "B · 小程序与现场"), ("#F59E0B", "共同")]],
              loc="lower right", fontsize=9.5)
    ax.set_title("8 周排期甘特图（2人团队·全功能）", fontsize=15, weight="bold", pad=14)
    fig.tight_layout()
    save(fig, "gantt.png")


# ---------------------------------------------------------------- 6 现场分区
def site_zones():
    fig, ax = newfig(12, 6.6)
    ax.text(50, 95, "现场分区布局与人员设备配置（单向动线）", ha="center", fontsize=16, weight="bold")

    zones = [
        (3, 45, 14, 34, "① 入口核验区\n动态码大屏(2s刷新)\nENTRY员工×2(半离线)\n异常登记本兜底", C_ZONE, E_ZONE),
        (20, 45, 16, 34, "② 排队通道\nQUEUE员工×3\n扫客户2FA验已下单\nAP-1覆盖", C_ZONE, E_ZONE),
        (39, 45, 17, 34, "③ 浏览/下单配货区\nQUEUE员工×2·打印机×2\n自动打小票交顾客\nAP-1/AP-3覆盖", C_ZONE, E_ZONE),
        (59, 45, 17, 34, "④ 提货区\nPICKUP员工×2\n扫2FA核销·按小票取货\n打印机×1(备用热备)·AP-2", C_ZONE, E_ZONE),
        (79, 45, 18, 34, "⑤ 出口纪念品区\nSOUVENIR员工×1\n扫2FA·指纹+wxid防重领\nAP-2覆盖", C_ZONE, E_ZONE),
    ]
    for x, y, w, h, t, fc, ec in zones:
        box(ax, x, y, w, h, t, fc, ec, 9.5)

    box(ax, 30, 12, 38, 14, "指挥台（ADMIN平板·监控大屏·备用件台）\n备用CPE/打印机/SIM·UPS·登记本·对讲机·Runbook", "#FEF3C7", "#D97706", 10)
    box(ax, 3, 12, 24, 14, "服务器区（隐蔽位）\nF1 .21 / F2 .22 / BE .23\n交换机×2 · UPS×3 · 运维本 .30", C_BE, E_BE, 9.5)

    for x in (10, 27, 47, 67, 87):
        ax.add_patch(Polygon([[x, 84.5], [x - 1.6, 81.5], [x + 1.6, 81.5]], closed=True, fc="#0EA5E9", ec="none"))
        ax.text(x, 79.8, "AP", ha="center", fontsize=8, color="#0EA5E9", weight="bold")

    for x1, x2 in [(17, 20), (36, 39), (56, 59), (76, 79)]:
        arrow(ax, x1 + 0.3, 62, x2 - 0.3, 62, "人流→", 9, loff=(0, 1.2))
    ax.text(50, 4, "总动线：入口 → 排队（可浏览下单）→ 配货打票 → 提货 → 出口领纪念品 ｜ 顾客端全程单店单订单+限购",
            ha="center", fontsize=10, color="#555")
    save(fig, "site_zones.png")


if __name__ == "__main__":
    arch_overview()
    network_topology()
    sequence_order()
    state_machine()
    gantt()
    site_zones()
    print("ALL DONE ->", os.path.abspath(OUT))
