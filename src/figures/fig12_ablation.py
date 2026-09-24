"""EXP-015c: visualización de salida existente, sin volver a simular."""
import hashlib
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, ".")
from src.figures import style as S

SOURCE = Path("work/mosaic/baf_ablation.json")
SHA256 = "27fdcb62b0f2c82ef6492081eff88bcf68290b9ebc2994df32d227a6eea22f19"


def load_and_build():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("Ablation source changed; review before rendering")
    data = json.loads(raw)
    cells = [c for c in data["cells"] if c["scope"] == "frac"]
    fig, axes = plt.subplots(2, 2, figsize=(11.8, 8.8), sharex=True, sharey=True)
    fig.subplots_adjust(left=.09, right=.97, top=.82, bottom=.22, hspace=.32, wspace=.15)
    fig.suptitle("Which factor changes the BAF readout?", x=.09, y=.95,
                 ha="left", fontsize=19, fontweight="bold", color=S.INK)
    fig.text(.09,.905,"EXP-015c · POST-HOC DIAGNOSTIC ABLATION · simulation, no patient data",
             fontsize=11, color=S.MUTED)
    stats = [("signed", "A · Absolute mean signed deviation"),
             ("absdev", "B · Mean absolute deviation"),
             ("disp", "C · Site-wise BAF variance"),
             ("znorm", "D · Mean absolute depth-standardised z")]
    for ax, (stat, title) in zip(axes.flat, stats):
        for direction, color in [("fixed", S.BLUE), ("mixed", S.VERM)]:
            for depth, line, marker in [("cn", "-", "o"), ("matched", "--", "s")]:
                rows = sorted([c for c in cells if c["direction"] == direction and
                               c["depth_model"] == depth], key=lambda c:c["fraction"])
                ax.plot([100*c["fraction"] for c in rows], [c["power_"+stat] for c in rows],
                        color=color, ls=line, marker=marker, markersize=4, lw=1.6,
                        markerfacecolor="white" if depth == "matched" else color)
        ax.axhline(data["alpha"], color=S.MUTED, ls=":", lw=1)
        ax.set_title(title, loc="left", fontsize=11, pad=12)
        ax.set_ylim(-.02,1.03)
        S.grid(ax)
    for ax in axes[1]: ax.set_xlabel("simulated affected-cell fraction (%)")
    for ax in axes[:,0]: ax.set_ylabel("empirical rejection proportion")
    handles = [Line2D([],[],color=S.BLUE,label="Fixed homolog direction"),
               Line2D([],[],color=S.VERM,label="Mixed homolog direction"),
               Line2D([],[],color=S.INK,marker="o",label="Copy-number-scaled depth"),
               Line2D([],[],color=S.INK,ls="--",marker="s",markerfacecolor="white",label="Depth matched to null")]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.115),ncol=2,frameon=False,fontsize=10)
    S.note(fig, f"Frozen source: work/mosaic/baf_ablation.json · sha256 {SHA256[:16]}... · seed {data['seed']}.\n"
           f"All scope=frac cells; four crossed conditions at every available fraction. {data['n_rep']} replicates per condition; "
           f"{data['n_sites']} sites/chromosome; null depth {data['depth']}x. Dotted line: alpha={data['alpha']}.\n"
           "Lines connect tested fractions only. No confidence intervals estimated here; small differences are not claimed as effects.\n"
           "scope=all clonal controls are not part of this factorial view. Diagnostic, not confirmatory; no patient mosaic fraction or superiority over phased methods.", y=.009)
    return fig, data


if __name__ == "__main__":
    fig, _ = load_and_build()
    S.export(fig, "fig12_baf_factorial_ablation", "SIMULATION", "SIMULATED")
    plt.close(fig)
