from libyana.visutils import detect2d


def add_hoa_viz(ax, hoa_df, resize_factor=1, debug=False):
    if hoa_df.shape[0] > 0:
        if debug:
            print("Drawing predicted hand and object boxes !")
        bboxes_norm = [
            [
                box_row[1].left * resize_factor,
                box_row[1].top * resize_factor,
                box_row[1].right * resize_factor,
                box_row[1].bottom * resize_factor,
            ]
            for box_row in hoa_df.iterrows()
        ]
        colors = [get_hoa_color(obj[1]) for obj in hoa_df.iterrows()]
        labels = [get_hoa_label(obj[1]) for obj in hoa_df.iterrows()]
        detect2d.visualize_bboxes(
            ax,
            bboxes_norm,
            labels=labels,
            label_color="w",
            linewidth=2,
            color=colors,
        )


def get_hoa_color(obj):
    if obj.det_type == "hand":
        if obj.side == "right":
            return "g"
        elif obj.side == "left":
            return "m"
    else:
        return "k"


def get_hoa_label(obj):
    if obj.det_type == "hand":
        if obj.side == "right":
            label = "hand_r"
        elif obj.side == "left":
            label = "hand_l"
        else:
            raise ValueError("hand side {obj.side} not in [left|right]")
        if "hoa_link" in obj.keys() and (obj.hoa_link == obj.hoa_link):
            hoa_label = obj.hoa_link[:5]
            label = label + hoa_label
    else:
        label = "obj"
    if "score" in obj.keys():
        label = label + ": {obj.score:.2f}"
    return label
