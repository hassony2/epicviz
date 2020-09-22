import numpy as np
from PIL import Image
from libyana.visutils import detect2d
from pycocotools.mask import decode as coco_mask_decode
from epic.masks import coco
from matplotlib import cm


def resize_mask(
    mask: np.ndarray, height: int, width: int, smooth: bool = True
) -> np.ndarray:
    assert mask.ndim == 2
    if smooth:
        # The original masks seem to be
        mask_img = Image.fromarray(mask * 255)
        return (
            np.asarray(
                mask_img.resize((50, 50), Image.LANCZOS).resize(
                    (width, height), Image.LANCZOS
                )
            )
            > 128
        ).astype(np.uint8)
    return np.asarray(Image.fromarray(mask).resize((width, height), Image.NEAREST))


def add_masks_viz(
    ax, masks_df, resize_factor=1, alpha_mask=0.3, debug=False, filter_person=True
):
    if masks_df.shape[0] > 0:
        if debug:
            print("Drawing predicted hand and object boxes !")
        bboxes_norm = [
            [
                box_row[1].left * resize_factor,
                box_row[1].top * resize_factor,
                box_row[1].right * resize_factor,
                box_row[1].bottom * resize_factor,
            ]
            for box_row in masks_df.iterrows()
        ]
        masks = [
            coco_mask_decode({"counts": row[1]["mask"], "size": [100, 100]})
            for row in masks_df.iterrows()
        ]
        masks = [
            resize_mask(
                mask, height=int(1080 * resize_factor), width=int(1920 * resize_factor)
            )
            for mask in masks
        ]

        colors = [get_masks_color(obj[1]) for obj in masks_df.iterrows()]
        labels = [get_masks_label(obj[1]) for obj in masks_df.iterrows()]
        if filter_person:
            # Remove person detections
            sel_idxs = [idx for idx, lab in enumerate(labels) if "person" not in lab]
            labels = [labels[sel_idx] for sel_idx in sel_idxs]
            colors = [colors[sel_idx] for sel_idx in sel_idxs]
            masks = [masks[sel_idx] for sel_idx in sel_idxs]
            bboxes_norm = [bboxes_norm[sel_idx] for sel_idx in sel_idxs]
        detect2d.visualize_bboxes(
            ax,
            bboxes_norm,
            labels=labels,
            label_color="w",
            linewidth=2,
            color=colors,
        )
        for label, mask in zip(labels, masks):
            base_mask = mask[:, :, np.newaxis].astype(np.float)
            show_mask = np.concatenate(
                [base_mask.repeat(3, 2), base_mask * alpha_mask], 2
            )
            ax.imshow(show_mask)


def get_masks_color(obj):
    return "c"


def get_masks_label(obj):
    label = coco.class_names[obj.pred_class]
    return f"{label}: {obj.score:.2f}"
