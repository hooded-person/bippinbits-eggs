import csv
import os
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.axes
import matplotlib.dates as mdates
import numpy as np
import datetime as dt

data = {
    "total": 0,
    "dpy": {},
    "year": {},
    "month": {},
    "all": {},
}


class Plot:
    def __init__(
        self,
        title: str,
        type: str = "plot",
        cat: str = "",
        clone: Optional[str] = None,
    ) -> None:
        self.title: str = title
        self.category: str = cat
        self.type: str = type
        self.clone: Optional[str] = clone
        self.x: List[Any] = []
        self.y: List[Any] = []

    def plot(self, ax: matplotlib.axes.Axes) -> None:
        # Use clone data if requested
        if self.clone:
            src = plots.get(self.clone)
            x = list(src.x) if src else []
            y = list(src.y) if src else []
        else:
            x = list(self.x)
            y = list(self.y)

        ax.set_title(self.title)

        # Empty data guard
        if (not hasattr(x, "__len__") or len(x) == 0) and (
            not hasattr(y, "__len__") or len(y) == 0
        ):
            return

        # Histogram modes — compute counts from x or y
        if self.type == "hist.x":
            vals, counts = np.unique(x, return_counts=True)
            ax.bar(vals, counts)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            # ensure integer ticks for categorical/numeric bins
            try:
                vals_arr = np.asarray(vals)
                if np.issubdtype(vals_arr.dtype, np.integer):
                    ax.set_xticks(vals_arr.tolist())
                    ax.set_xlim(vals_arr.min() - 0.5, vals_arr.max() + 0.5)
            except Exception:
                pass
            return
        if self.type == "hist.y":
            vals, counts = np.unique(y, return_counts=True)
            ax.bar(vals, counts)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            try:
                vals_arr = np.asarray(vals)
                if np.issubdtype(vals_arr.dtype, np.integer):
                    ax.set_xticks(vals_arr.tolist())
                    ax.set_xlim(vals_arr.min() - 0.5, vals_arr.max() + 0.5)
            except Exception:
                pass
            return

        # Convert date x-values to matplotlib numeric dates if needed
        is_date_axis = False
        if hasattr(x, "__len__") and len(x) > 0 and isinstance(x[0], dt.date):
            is_date_axis = True
            orig_dates = list(x)
            x = mdates.date2num(x)
            ax.xaxis_date()
            # choose locator based on span
            span_days = (
                (max(orig_dates) - min(orig_dates)).days if len(orig_dates) > 1 else 0
            )
            if span_days <= 31:
                locator = mdates.DayLocator(interval=max(1, span_days // 7))
            elif span_days <= 366:
                locator = mdates.MonthLocator()
            else:
                locator = mdates.YearLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))

        # Draw requested plot type
        if self.type == "bar":
            ax.bar(x, y)
        elif self.type == "scatter":
            ax.scatter(x, y)
        elif self.type == "timeseries":
            # line plot with markers, works for dates or numeric x
            ax.plot(x, y, "-o", linewidth=1, markersize=4)
        else:
            # fallback to calling the axis method if available
            func = getattr(ax, self.type, None)
            if callable(func):
                func(x, y)
            else:
                ax.plot(x, y)

        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # X axis formatting for integers or strings
        if hasattr(x, "__len__") and len(x) > 0:
            sample = x[0]
            # integer-like categorical axis
            if isinstance(sample, (int, np.integer)):
                ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            else:
                ax.tick_params(axis="x", rotation=45)


cat_order = ["Summary", "This Month", "This Year", "All Time"]
plots: Dict[str, Plot] = {
    "thisYear": Plot("This Year", "timeseries", cat="This Year"),
    "thisYearPerMonth": Plot("Per Month", "bar", cat="This Year"),
    "thisYearCumulative": Plot("Cumulative This Year", "timeseries", cat="This Year"),
    "thisYearRolling7": Plot("7-day rolling average", "timeseries", cat="This Year"),
    "eggsPerWeek": Plot("Eggs per Week", "bar", cat="This Year"),
    "thisYearEggCountDistribution": Plot(
        "Egg count distribution (this year)",
        "hist.y",
        cat="This Year",
    ),
    "thisMonth": Plot("This Month", "timeseries", cat="This Month"),
    "thisMonthEggCountDistribution": Plot(
        "Egg count distribution (this month)",
        "hist.y",
        cat="This Month",
    ),
    "allTimeEggCountDistribution": Plot(
        "Egg count distribution (all time)",
        "hist.y",
        cat="All Time",
    ),
}

# today and window for "this month"
_TODAY = dt.date.today()
_MONTH_WINDOW = dt.timedelta(days=30)

with open("eggs.csv", newline="") as file:
    reader = csv.reader(file)
    reader.__next__()  # skip headers
    for row in reader:
        dateStr, eggs = row
        date = None
        # try common date formats
        for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                date_dt = dt.datetime.strptime(dateStr, fmt)
                date = date_dt.date()
                break
            except Exception:
                pass
        if date is None:
            # fallback: try splitting on separators
            parts = dateStr.replace("-", "/").split("/")
            if len(parts) == 3:
                try:
                    d, m, y = parts
                    day, month, year = int(d), int(m), int(y)
                    date = dt.date(year=year, month=month, day=day)
                except Exception:
                    # skip malformed line
                    continue
            else:
                continue
        # extract year/month/day for downstream aggregation
        day, month, year = date.day, date.month, date.year

        try:
            eggs = int(eggs)
        except Exception:
            continue

        data["all"][dateStr] = eggs
        data["total"] = data.get("total", 0) + eggs
        data["dpy"][year] = data["dpy"].get(year, 0) + 1
        data["year"][year] = data["year"].get(year, 0) + eggs
        if not year in data["month"]:
            data["month"][year] = {}
        data["month"][year][month] = data["month"][year].get(month, 0) + eggs

        if date.year == _TODAY.year:
            plots["thisYear"].x.append(date)
            plots["thisYear"].y.append(eggs)
            plots["thisYearEggCountDistribution"].y.append(eggs)
        # thisMonth: use recent 30-day window rather than calendar month
        if date >= (_TODAY - _MONTH_WINDOW) and date <= _TODAY:
            plots["thisMonth"].x.append(date)
            plots["thisMonth"].y.append(eggs)
            plots["thisMonthEggCountDistribution"].y.append(eggs)

        plots["allTimeEggCountDistribution"].y.append(eggs)

# processing

if plots["thisYear"].y:
    # aggregate monthly totals
    months = np.array([d.month for d in plots["thisYear"].x])
    values = np.array(plots["thisYear"].y)
    monthly_totals = np.bincount(months, weights=values, minlength=13)[1:]
    plots["thisYearPerMonth"].x = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    plots["thisYearPerMonth"].y = list(monthly_totals)

    # cumulative over sorted dates
    pairs = sorted(zip(plots["thisYear"].x, plots["thisYear"].y))
    if pairs:
        dates_sorted, eggs_sorted = zip(*pairs)
        cum = np.cumsum(np.array(eggs_sorted))
        plots["thisYearCumulative"].x = list(dates_sorted)
        plots["thisYearCumulative"].y = cum.tolist()

        # 7-day rolling average on the ordered points (simple convolution)
        window = 7
        vals = np.array(eggs_sorted)
        if vals.size > 0:
            kernel = np.ones(window) / window
            roll = np.convolve(vals, kernel, mode="same")
            plots["thisYearRolling7"].x = list(dates_sorted)
            plots["thisYearRolling7"].y = roll.tolist()

        # eggs per ISO week
        week_sums: Dict[str, int] = {}
        for d, e in zip(dates_sorted, eggs_sorted):
            wy = d.isocalendar()  # (year, week, weekday)
            key = f"{wy[0]}-W{wy[1]:02d}"
            week_sums[key] = week_sums.get(key, 0) + int(e)
        # sort by year-week key
        week_items = sorted(week_sums.items(), key=lambda t: t[0])
        if week_items:
            plots["eggsPerWeek"].x = [k for k, _ in week_items]
            plots["eggsPerWeek"].y = [v for _, v in week_items]

# drawing

# ensure images dir exists
os.makedirs("images", exist_ok=True)

for plot_id, plot in plots.items():
    # make 'thisYear' and 'thisMonth' less tall to reduce vertical whitespace
    if plot_id in ("thisYear", "thisMonth"):
        fig, ax = plt.subplots(figsize=(8, 2.6))
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
    plot.plot(ax)
    # format date labels and prevent clipping
    try:
        fig.autofmt_xdate()
    except Exception:
        pass
    plt.tight_layout()
    plt.savefig(os.path.join("images", f"{plot_id}.png"), bbox_inches="tight")
    plt.close(fig)

by_cat = {}
for id in plots:
    plot = plots[id]
    try:
        by_cat[plot.category].append(id)
    except KeyError:
        by_cat[plot.category] = [id]

with open("GRAPHS.md", "w") as file:
    # summary stats
    total_all = data.get("total", 0)
    total_this_year = data.get("year", {}).get(_TODAY.year, 0)
    days_this_year = data.get("dpy", {}).get(_TODAY.year, 0)
    avg_per_day = total_this_year / days_this_year if days_this_year else 0

    print(f"# Summary", file=file)
    print(f"- **Total eggs (all time):** {total_all}", file=file)
    print(f"- **Total eggs ({_TODAY.year}):** {total_this_year}", file=file)
    print(f"- **Days recorded ({_TODAY.year}):** {days_this_year}", file=file)
    print(f"- **Average eggs/day ({_TODAY.year}):** {avg_per_day:.2f}", file=file)
    print("", file=file)

    # per-category graphs
    for cat in cat_order[1:]:
        print(f"# {cat}", file=file)
        for id in by_cat.get(cat, []):
            plot = plots[id]
            print(f"![{plot.title}](/images/{id}.png)", file=file)
