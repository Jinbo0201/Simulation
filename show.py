import sys
import pandas as pd
import pygame
import os


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
    # default to file in docs directory if no argument given
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "data_2026-02-28_10-43-42.csv"

    # ensure path is in docs
    current_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(current_dir, 'docs')
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(docs_dir, csv_path)

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

    # single segment display (no tiling)
    segments = 1
    # compute length of road
    seg_length = max_x if max_x > 0 else 0

    # widen display and slightly reduce lane height
    screen_width = 1200
    lane_height = 30
    # height of the display covering all lanes
    screen_height = lane_height * lanes + 40
    seg_width = screen_width
    # scale for converting x to pixels across the full road length
    scale = seg_width / seg_length if seg_length > 0 else 1

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("车辆轨迹展示")
    clock = pygame.time.Clock()
    # frames per second for the animation; lower values = slower
    fps = 1

    times = sorted(df["simTime"].unique())
    # precompute min/max speeds for optional shading
    v_min = df["v"].min()
    v_max = df["v"].max()

    # richer coloring: assign each vehicle a base color from a palette
    palette = [
        (255, 0, 0),     # red
        (0, 255, 0),     # green
        (0, 0, 255),     # blue
        (255, 255, 0),   # yellow
        (255, 0, 255),   # magenta
        (0, 255, 255),   # cyan
        (255, 165, 0),   # orange
        (128, 0, 128),   # purple
    ]
    color_map = {}

    def base_color_for_id(veh_id):
        # pick the next color in the palette (wrap around)
        if veh_id not in color_map:
            color_map[veh_id] = palette[len(color_map) % len(palette)]
        return color_map[veh_id]

    def shade_color(color, v):
        # optionally make the color lighter/darker based on speed
        if v_max == v_min:
            return color
        ratio = (v - v_min) / (v_max - v_min)
        # interpolate between 50% and 150% brightness
        factor = 0.5 + ratio
        return tuple(max(0, min(255, int(c * factor))) for c in color)

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
        # draw lane areas across full height
        for i in range(lanes):
            lane_rect = pygame.Rect(0, i * lane_height, seg_width, lane_height)
            color = (50, 50, 50) if i % 2 == 0 else (60, 60, 60)
            pygame.draw.rect(screen, color, lane_rect)
        # draw lane divider lines
        for i in range(lanes + 1):
            y = i * lane_height
            pygame.draw.line(screen, (200, 200, 200), (0, y), (seg_width, y), 1)
        # draw vehicles with color based on speed
        for _, row in subset.iterrows():
            # pixel x calculated over full road
            x_pix = int(row["x"] * scale)
            lane_idx = int(row["laneNum"] - 1)
            # make vehicle even smaller
            veh_w = 4
            veh_h = int(lane_height * 0.3)
            y_pix = lane_idx * lane_height + (lane_height - veh_h) // 2
            rect = pygame.Rect(x_pix, y_pix, veh_w, veh_h)
            # choose a base color for the vehicle id, then shade by speed
            base = base_color_for_id(row["id"])
            color = shade_color(base, row["v"])
            pygame.draw.rect(screen, color, rect)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
