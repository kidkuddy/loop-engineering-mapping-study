#!/usr/bin/env python3
"""Build the systematic map: facet distributions, cross-tabulations, and the
bubble plot that is Petersen's signature output.

Reads the adjudicated facet assignments from the database. Writes:
  coding/map-<axis>.csv          one distribution per axis
  coding/crosstab-*.csv          the cross-tabulations the paper reports
  figures/bubble.pdf             loop_mechanism x {contribution_type, research_type}
  figures/evidence.pdf           evaluation_strategy by loop_mechanism
"""
import collections, csv, os, sqlite3, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite"))
T = 1
FIG = os.path.join(ROOT, "figures"); os.makedirs(FIG, exist_ok=True)

AXES = ["loop_mechanism", "contribution_type", "research_type",
        "evaluation_strategy", "human_role", "venue_type"]
ORDER = {a: [v.strip() for v in con.execute(
    "SELECT allowed FROM facet_schemes WHERE topic_id=? AND axis=?", (T, a)
).fetchone()[0].split(",")] for a in AXES}

lab = collections.defaultdict(dict)
for pid, axis, val in con.execute(
        """SELECT paper_id, axis, value FROM facet_assignments
           WHERE topic_id=? AND assigned_by='adjudicated'""", (T,)):
    lab[pid][axis] = val
if not lab:
    sys.exit("no adjudicated facet assignments yet")
print(f"papers with adjudicated labels: {len(lab)}")

for a in AXES:
    c = collections.Counter(v.get(a) for v in lab.values() if v.get(a))
    with open(os.path.join(ROOT, "coding", f"map-{a}.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow([a, "n", "pct"])
        tot = sum(c.values())
        for val in ORDER[a]:
            w.writerow([val, c.get(val, 0), f"{100.0*c.get(val,0)/max(tot,1):.1f}"])
    print(f"  {a:24s} " + "  ".join(f"{v}={c.get(v,0)}" for v in ORDER[a]))

def crosstab(ax, ay, name):
    t = collections.Counter((v.get(ax), v.get(ay)) for v in lab.values()
                            if v.get(ax) and v.get(ay))
    with open(os.path.join(ROOT, "coding", f"crosstab-{name}.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow([ax] + ORDER[ay])
        for x in ORDER[ax]:
            w.writerow([x] + [t.get((x, y), 0) for y in ORDER[ay]])
    return t

ct_contrib = crosstab("loop_mechanism", "contribution_type", "mechanism-contribution")
ct_res = crosstab("loop_mechanism", "research_type", "mechanism-researchtype")
ct_eval = crosstab("loop_mechanism", "evaluation_strategy", "mechanism-evaluation")
crosstab("loop_mechanism", "human_role", "mechanism-humanrole")
crosstab("research_type", "evaluation_strategy", "researchtype-evaluation")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("matplotlib missing -- CSVs written, figures skipped")

SHORT = {
    "verification_and_gating": "verification\n& gating",
    "critique_and_revision": "critique\n& revision",
    "loop_evaluation_and_diagnosis": "loop evaluation\n& diagnosis",
    "multi_agent_coordination": "multi-agent\ncoordination",
    "planning_and_control_flow": "planning &\ncontrol flow",
    "deliberative_search": "deliberative\nsearch",
    "self_evolution": "self-evolution",
    "memory_and_context_management": "memory &\ncontext mgmt",
    "budget_and_termination_control": "budget &\ntermination",
}
mech = [m for m in ORDER["loop_mechanism"]]
ylab = [SHORT.get(m, m) for m in mech]

def bubble(ax_, tab, cols, title, invert):
    xs, ys, ss, labels = [], [], [], []
    for j, c in enumerate(cols):
        for i, m in enumerate(mech):
            n = tab.get((m, c), 0)
            if n:
                xs.append(j); ys.append(i); ss.append(n); labels.append(n)
    mx = max(ss) if ss else 1
    ax_.scatter(xs, ys, s=[40 + 1500.0 * v / mx for v in ss],
                facecolor="#4C72B0", alpha=.55, edgecolor="#20355c", linewidth=.7, zorder=3)
    for x, y, n in zip(xs, ys, labels):
        ax_.text(x, y, str(n), ha="center", va="center", fontsize=6.4,
                 color="#10203d", zorder=4)
    ax_.set_xticks(range(len(cols)))
    ax_.set_xticklabels([c.replace("_", "\n") for c in cols], fontsize=7, rotation=0)
    ax_.set_yticks(range(len(mech)))
    ax_.set_xlim(-0.7, len(cols) - 0.3); ax_.set_ylim(-0.7, len(mech) - 0.3)
    ax_.grid(True, which="major", color="#dddddd", linewidth=.6, zorder=0)
    ax_.set_axisbelow(True)
    ax_.set_title(title, fontsize=8.5, pad=6)
    for s in ax_.spines.values():
        s.set_color("#999999")
    if invert:
        ax_.invert_xaxis()
        ax_.yaxis.tick_right()
    ax_.set_yticklabels([])

fig, (l, r) = plt.subplots(1, 2, figsize=(7.1, 4.3), sharey=True,
                           gridspec_kw={"wspace": .46})
bubble(l, ct_contrib, ORDER["contribution_type"], "Contribution type", True)
bubble(r, ct_res, ORDER["research_type"], "Research type", False)
for i, t in enumerate(ylab):
    fig.text(.5, 0, "", fontsize=1)
    l.text(len(ORDER["contribution_type"]) - 0.5 + 0.15, i, t, ha="center", va="center",
           fontsize=6.6, transform=l.transData)
fig.savefig(os.path.join(FIG, "bubble.pdf"), bbox_inches="tight")
print(f"wrote {FIG}/bubble.pdf")

fig2, ax2 = plt.subplots(figsize=(7.1, 3.1))
ev = ORDER["evaluation_strategy"]
bottom = [0] * len(mech)
cmap = plt.get_cmap("Blues")
for k, e in enumerate(ev):
    vals = [ct_eval.get((m, e), 0) for m in mech]
    ax2.bar(range(len(mech)), vals, bottom=bottom, label=e.replace("_", " "),
            color=cmap(0.25 + 0.7 * k / max(len(ev) - 1, 1)),
            edgecolor="white", linewidth=.5)
    bottom = [b + v for b, v in zip(bottom, vals)]
ax2.set_xticks(range(len(mech)))
ax2.set_xticklabels([m.replace("_and_", " &\n").replace("_", " ") for m in mech],
                    fontsize=6.3)
ax2.set_ylabel("papers", fontsize=8)
ax2.legend(fontsize=6.2, ncol=4, frameon=False, loc="upper center",
           bbox_to_anchor=(.5, 1.22))
ax2.tick_params(labelsize=7)
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)
fig2.savefig(os.path.join(FIG, "evidence.pdf"), bbox_inches="tight")
print(f"wrote {FIG}/evidence.pdf")
