"""
ASCII chart generation for English Buddy.
Creates terminal-friendly visualizations.
"""


def ascii_bar_chart(data: dict, title: str = "", width: int = 40) -> str:
    """
    Generate an ASCII horizontal bar chart.

    Args:
        data: Dict of {label: value}
        title: Chart title
        width: Maximum bar width in characters

    Returns:
        Formatted ASCII chart string
    """
    if not data:
        return "No data available"

    lines = []

    if title:
        lines.append(title)
        lines.append("━" * len(title))

    # Find max value for scaling
    max_value = max(data.values()) if data.values() else 1
    total = sum(data.values())

    # Find max label length for alignment
    max_label_len = max(len(str(k)) for k in data.keys())

    for label, value in data.items():
        # Calculate bar length
        if max_value > 0:
            bar_len = int((value / max_value) * width)
        else:
            bar_len = 0

        # Calculate percentage
        if total > 0:
            pct = (value / total) * 100
        else:
            pct = 0

        # Create bar
        bar = "█" * bar_len

        # Format line
        label_padded = str(label).ljust(max_label_len)
        lines.append(f"{label_padded}  {bar} {value} ({pct:.0f}%)")

    return "\n".join(lines)


def ascii_trend_chart(data: list, title: str = "", height: int = 8) -> str:
    """
    Generate an ASCII line/trend chart.

    Args:
        data: List of (label, value) tuples
        title: Chart title
        height: Chart height in lines

    Returns:
        Formatted ASCII chart string
    """
    if not data:
        return "No data available"

    lines = []

    if title:
        lines.append(title)
        lines.append("━" * len(title))

    values = [v for _, v in data]
    labels = [l for l, _ in data]

    max_val = max(values) if values else 1
    min_val = min(values) if values else 0

    # Build the chart rows
    for row in range(height, 0, -1):
        threshold = min_val + (max_val - min_val) * (row / height)
        line = ""
        for val in values:
            if val >= threshold:
                line += "█"
            else:
                line += " "
        # Add Y-axis label for top and bottom
        if row == height:
            lines.append(f"{max_val:>4} │{line}")
        elif row == 1:
            lines.append(f"{min_val:>4} │{line}")
        else:
            lines.append(f"     │{line}")

    # X-axis
    lines.append("     └" + "─" * len(values))

    # Labels (abbreviated)
    label_line = "      "
    for label in labels:
        label_line += label[0] if label else " "
    lines.append(label_line)

    return "\n".join(lines)


def progress_indicator(current: int, total: int, width: int = 20) -> str:
    """
    Generate a progress bar.

    Args:
        current: Current value
        total: Total/target value
        width: Bar width

    Returns:
        Progress bar string
    """
    if total <= 0:
        return "[" + " " * width + "] 0%"

    pct = min(current / total, 1.0)
    filled = int(pct * width)
    empty = width - filled

    return f"[{'█' * filled}{'░' * empty}] {pct * 100:.0f}%"


def summary_box(title: str, items: list) -> str:
    """
    Generate a summary box with items.

    Args:
        title: Box title
        items: List of strings to display

    Returns:
        Formatted box string
    """
    lines = []

    # Calculate width
    max_item_len = max(len(str(item)) for item in items) if items else 0
    width = max(len(title), max_item_len) + 4

    # Top border
    lines.append("┌" + "─" * width + "┐")

    # Title
    lines.append("│ " + title.center(width - 2) + " │")
    lines.append("├" + "─" * width + "┤")

    # Items
    for item in items:
        lines.append("│ " + str(item).ljust(width - 2) + " │")

    # Bottom border
    lines.append("└" + "─" * width + "┘")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test charts
    print("\n=== Bar Chart Test ===")
    data = {
        "Spelling": 25,
        "Grammar": 50,
        "Style": 15,
        "Vocabulary": 10
    }
    print(ascii_bar_chart(data, "Error Distribution"))

    print("\n=== Trend Chart Test ===")
    trend_data = [
        ("Mon", 5),
        ("Tue", 8),
        ("Wed", 3),
        ("Thu", 10),
        ("Fri", 6),
        ("Sat", 2),
        ("Sun", 4)
    ]
    print(ascii_trend_chart(trend_data, "Weekly Errors"))

    print("\n=== Summary Box Test ===")
    print(summary_box("Today's Stats", [
        "Total: 8 corrections",
        "Spelling: 2",
        "Grammar: 5",
        "Style: 1"
    ]))
