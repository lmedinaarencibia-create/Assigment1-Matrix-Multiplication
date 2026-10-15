import argparse, json, os, platform, shutil, subprocess, sys, time, threading, statistics, pathlib
from datetime import datetime
import psutil

ROOT=pathlib.Path(__file__).resolve().parent
RESULTS=ROOT/"results"
RESULTS.mkdir(exist_ok=True)

def run_monitored(cmd, timeout):
    proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT)
    peak=0
    deadline=time.monotonic()+timeout
    try:
        p=psutil.Process(proc.pid)
        while proc.poll() is None:
            if time.monotonic() > deadline:
                proc.kill()
                proc.communicate()
                raise subprocess.TimeoutExpired(cmd, timeout)
            try:
                rss=p.memory_info().rss
                peak=max(peak,rss)
                for child in p.children(recursive=True):
                    try: peak=max(peak,child.memory_info().rss)
                    except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            time.sleep(0.01)
        out,err=proc.communicate(timeout=2)
    except Exception:
        proc.kill()
        out,err=proc.communicate()
        raise
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{err}\n{out}")
    return json.loads(out.strip().splitlines()[-1]), peak

def quantile(sorted_vals, q):
    if not sorted_vals: return float("nan")
    pos=(len(sorted_vals)-1)*q
    lo=int(pos); hi=min(lo+1,len(sorted_vals)-1)
    return sorted_vals[lo]+(sorted_vals[hi]-sorted_vals[lo])*(pos-lo)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sizes",default="16,32,64,96,128")
    ap.add_argument("--repetitions",type=int,default=5)
    ap.add_argument("--warmups",type=int,default=2)
    ap.add_argument("--timeout",type=int,default=60)
    args=ap.parse_args()
    sizes=[int(x) for x in args.sizes.split(",") if x.strip()]
    if not sizes or any(n<1 for n in sizes): raise SystemExit("Sizes must be positive integers.")
    java=shutil.which("java"); javac=shutil.which("javac"); gcc=shutil.which("gcc")
    if not java or not javac: raise SystemExit("Java/Javac not found on PATH.")
    if not gcc: raise SystemExit("gcc not found on PATH. Install GCC and add it to PATH.")
    subprocess.run([javac,"java/MatrixMultiply.java"],check=True,cwd=ROOT)
    cexe=ROOT/("c/matrix_multiply.exe" if os.name=="nt" else "c/matrix_multiply")
    subprocess.run([gcc,"-O2","-std=c11","c/matrix_multiply.c","-o",str(cexe)],check=True,cwd=ROOT)
    env_lines=[
        "Timestamp: "+datetime.now().astimezone().isoformat(),
        "OS: "+platform.platform(),
        "CPU: "+platform.processor(),
        "Logical CPUs: "+str(os.cpu_count()),
        "Physical cores: "+str(psutil.cpu_count(logical=False)),
        "RAM total (GiB): "+f"{psutil.virtual_memory().total/1024**3:.2f}",
        "Python: "+sys.version.replace("\n"," "),
        "Python implementation: "+platform.python_implementation(),
        "Java: "+subprocess.check_output([java,"-version"],stderr=subprocess.STDOUT,text=True).splitlines()[0],
        "C compiler: "+subprocess.check_output([gcc,"--version"],text=True).splitlines()[0],
        "C flags: -O2 -std=c11",
        "Java flags: javac defaults; no explicit JVM flags",
        f"Warm-ups per size/method: {args.warmups}",
        f"Measured repetitions per size/method: {args.repetitions}",
        f"Timeout per process/configuration: {args.timeout} seconds",
        "Memory metric: peak process RSS sampled every 10 ms using psutil; sampling may miss short peaks.",
        "Timing boundary: multiplication kernel; input generation is outside timed region. Output allocation is included in Python/Java/C kernel as each multiply allocates result matrix.",
        "Input generation: deterministic formulas documented in README; same logical double-valued matrices across languages."
    ]
    (RESULTS/"environment.txt").write_text("\n".join(env_lines)+"\n",encoding="utf-8")
    raw=[]; summaries=[]; checks={}
    methods=[
      ("Python",[sys.executable,"python/multiply.py"]),
      ("Java",[java,"-Xms64m","-Xmx2g","-cp","java","MatrixMultiply"]),
      ("C",[str(cexe)])
    ]
    for n in sizes:
      for lang,basecmd in methods:
        cmd=basecmd+([ "--n",str(n),"--repetitions",str(args.repetitions),"--warmups",str(args.warmups)] if lang=="Python" else [str(n),str(args.repetitions),str(args.warmups)])
        start=time.perf_counter()
        try:
            data,peak=run_monitored(cmd,args.timeout)
            times=data["times_seconds"]; check=float(data["checksum"])
            checks[(n,lang)]=check
            for rep,t in enumerate(times,1):
                raw.append({"n":n,"language":lang,"repetition":rep,"time_seconds":t,"peak_rss_bytes_sampled":peak,"checksum":check,"status":"ok"})
            sv=sorted(times)
            summaries.append({"n":n,"language":lang,"repetitions":len(times),"median_seconds":statistics.median(times),
                              "iqr_seconds":quantile(sv,.75)-quantile(sv,.25),"peak_rss_mib_sampled":peak/1024**2,
                              "checksum":check,"status":"ok"})
            print(f"{lang:6s} n={n:4d} median={statistics.median(times):.6f}s peakRSS~{peak/1024**2:.1f} MiB")
        except subprocess.TimeoutExpired:
            raw.append({"n":n,"language":lang,"repetition":"","time_seconds":"","peak_rss_bytes_sampled":"","checksum":"","status":f"timeout>{args.timeout}s"})
            summaries.append({"n":n,"language":lang,"repetitions":0,"median_seconds":"","iqr_seconds":"","peak_rss_mib_sampled":"","checksum":"","status":f"timeout>{args.timeout}s"})
            print(f"{lang} n={n}: timeout")
        except Exception as e:
            raw.append({"n":n,"language":lang,"repetition":"","time_seconds":"","peak_rss_bytes_sampled":"","checksum":"","status":"error: "+str(e).replace("\n"," ")})
            summaries.append({"n":n,"language":lang,"repetitions":0,"median_seconds":"","iqr_seconds":"","peak_rss_mib_sampled":"","checksum":"","status":"error"})
            print(f"{lang} n={n}: ERROR {e}")
    correctness=[]
    for n in sizes:
        vals=[checks[(n,l)] for l in ("Python","Java","C") if (n,l) in checks]
        passed=(len(vals)==3 and max(vals)-min(vals) <= 1e-7*max(1.0,max(abs(x) for x in vals)))
        correctness.append({"n":n,"all_three_completed":len(vals)==3,"checksum_cross_language_pass":passed,
                            "checksums":";".join(f"{x:.12g}" for x in vals)})
    def write_csv(path,rows):
        if not rows: return
        import csv
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    write_csv(RESULTS/"raw_measurements.csv",raw)
    write_csv(RESULTS/"summary.csv",summaries)
    write_csv(RESULTS/"correctness.csv",correctness)
  
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        df=pd.DataFrame(summaries)
        good=df[df.status=="ok"].copy()
        good["median_seconds"]=pd.to_numeric(good["median_seconds"])
        good["peak_rss_mib_sampled"]=pd.to_numeric(good["peak_rss_mib_sampled"])
        fig,ax=plt.subplots()
        for lang,g in good.groupby("language"):
            ax.plot(g.n,g.median_seconds,marker="o",label=lang)
        ax.set_xlabel("Matrix side length n"); ax.set_ylabel("Median multiplication time (seconds)")
        ax.set_title("Basic matrix multiplication: runtime"); ax.grid(True,alpha=.3); ax.legend()
        fig.tight_layout(); fig.savefig(RESULTS/"runtime_plot.png",dpi=160); plt.close(fig)
        fig,ax=plt.subplots()
        for lang,g in good.groupby("language"):
            ax.plot(g.n,g.peak_rss_mib_sampled,marker="o",label=lang)
        ax.set_xlabel("Matrix side length n"); ax.set_ylabel("Peak process RSS sampled (MiB)")
        ax.set_title("Basic matrix multiplication: memory"); ax.grid(True,alpha=.3); ax.legend()
        fig.tight_layout(); fig.savefig(RESULTS/"memory_plot.png",dpi=160); plt.close(fig)
    except Exception as e: print("Plot generation issue:",e)
  
    lines=["Results generated from the local experiment","",
           "This file is generated from the measurements in `summary.csv`. Do not replace failed runs with estimated values.","",
           "Summary","",
           "| n | Language | Repetitions | Median (s) | IQR (s) | Peak RSS sampled (MiB) | Status |",
           "|---:|---|---:|---:|---:|---:|---|"]
    for r in summaries:
        lines.append(f"| {r['n']} | {r['language']} | {r['repetitions']} | {r['median_seconds']} | {r['iqr_seconds']} | {r['peak_rss_mib_sampled']} | {r['status']} |")
    lines += ["","Correctness checks","","| n | All three completed | Cross-language checksum passed | Checksums |","|---:|---|---|---|"]
    for r in correctness: lines.append(f"| {r['n']} | {r['all_three_completed']} | {r['checksum_cross_language_pass']} | {r['checksums']} |")
    successful=[r for r in summaries if r["status"]=="ok"]
    if successful:
        fastest_by_n=[]
        for n in sizes:
            rows=[r for r in successful if r["n"]==n]
            if rows:
                best=min(rows,key=lambda x:float(x["median_seconds"]))
                fastest_by_n.append(f"At n={n}, the lowest observed median was {best['language']} ({float(best['median_seconds']):.6g} s).")
        lines += ["","Observations based on this run",""]+fastest_by_n
        lines += ["","Interpret these findings only for this machine, these sizes, these implementations and these settings. Check correctness results before drawing conclusions. The three-loop algorithm performs O(n³) arithmetic work; measured times can deviate from a simple cubic curve because of fixed overhead, memory allocation, interpreter/runtime effects and hardware behaviour."]
    (RESULTS/"report_results.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\nResults saved in:",RESULTS)

if __name__=="__main__": main()
