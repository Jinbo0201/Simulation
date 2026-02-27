import sys
import pandas as pd
import pygame

"""Simple trajectory visualizer using pygame.

Usage:
    python show.py data_<timestamp>.csv

Reads the CSV produced by `SimControl.saveTraList` and animates
vehicle positions on a multi-lane road. X coordinates are scaled to
fit a fixed window width. The road is split into three equal-length
segments which are tiled side-by-side rather than drawn as a single
straight lane, allowing visualization of long stretches within the
display.
"""

def main():
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "data_2026-02-26_15-27-18.csv"

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Failed to read {csv_path}: {e}")
        sys.exit(1)

    if df.empty:
        print("Empty trajectory file")
        sys.exit(1)

    # determine layout
    max_x = df["x"].max()
    lanes = int(df["laneNum"].max())

    # We'll split the road (x range) into three segments and tile them
    # vertically (top/middle/bottom).
    segments = 3
    # compute length of each logical segment
    seg_length = max_x / segments if max_x > 0 else 0

    # widen display and slightly reduce lane height
    screen_width = 1200
    lane_height = 30
    # height of one segment containing all lanes
    seg_height = lane_height * lanes
    # total screen height needs room for all segments
    screen_height = seg_height * segments + 40
    # each segment spans the full width
    seg_width = screen_width
    # scale for converting x to pixels within a segment
    scale = seg_width / seg_length if seg_length > 0 else 1

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("车辆轨迹展示")
    clock = pygame.time.Clock()

    times = sorted(df["simTime"].unique())
    # precompute min/max speeds for coloring
    v_min = df["v"].min()
    v_max = df["v"].max()
    def speed_to_color(v):
        # map speed to a gradient from blue (slow) to red (fast)
        if v_max == v_min:
            return (0, 255, 0)
        ratio = (v - v_min) / (v_max - v_min)
        r = int(255 * ratio)
        b = int(255 * (1 - ratio))
        return (r, 0, b)

    running = True
    for t in times:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        if not running:
            break

        subset = df[df["simTime"] == t]

        # draw
        screen.fill((30, 30, 30))  # dark background
        # draw lane areas for each segment stacked vertically
        for seg in range(segments):
            y_offset = seg * seg_height
            for i in range(lanes):
                lane_rect = pygame.Rect(0, y_offset + i * lane_height, seg_width, lane_height)
                color = (50, 50, 50) if (i + seg) % 2 == 0 else (60, 60, 60)
                pygame.draw.rect(screen, color, lane_rect)
        # draw lane divider lines within each segment
        for seg in range(segments):
            y_offset = seg * seg_height
            for i in range(lanes + 1):
                y = y_offset + i * lane_height
                pygame.draw.line(screen, (200, 200, 200), (0, y), (seg_width, y), 1)
        # draw horizontal separators between segments (make them more visible)
        for seg in range(1, segments):
            y_sep = seg * seg_height
            # draw a thick bright line
            pygame.draw.line(screen, (255, 255, 255), (0, y_sep), (screen_width, y_sep), 4)
            # optionally draw a faint darker band above and below for emphasis
            band = 3
            pygame.draw.line(screen, (100, 100, 100), (0, y_sep - band), (screen_width, y_sep - band), 1)
            pygame.draw.line(screen, (100, 100, 100), (0, y_sep + band), (screen_width, y_sep + band), 1)
        # draw vehicles with color based on speed
        for _, row in subset.iterrows():
            # determine which segment the vehicle belongs to
            seg = int(row["x"] / seg_length) if seg_length > 0 else 0
            if seg >= segments:
                seg = segments - 1
            # pixel x within segment
            local_x = row["x"] - seg * seg_length
            x_pix = int(local_x * scale)
            lane_idx = int(row["laneNum"] - 1)
            # compute y offset for segment
            y_offset = seg * seg_height
            # make vehicle even smaller
            veh_w = 4
            veh_h = int(lane_height * 0.3)
            y_pix = y_offset + lane_idx * lane_height + (lane_height - veh_h) // 2
            rect = pygame.Rect(x_pix, y_pix, veh_w, veh_h)
            color = speed_to_color(row["v"])
            pygame.draw.rect(screen, color, rect)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()


if __name__ == "__main__":
    main()
